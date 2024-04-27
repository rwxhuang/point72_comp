import os
import googlemaps
from csp_bike import get_stations_df
import pandas as pd
import math
from functools import lru_cache
import datetime

maps_client = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])

# Get biking distance between two locations
@lru_cache
def get_distance_by_mode(ori_lat, ori_lng, dest_lat, dest_lng, mode):
    if mode == 'b':
        mode = 'bicycling'
    elif mode == 'd':
        mode = 'driving'

    distance = maps_client.distance_matrix(
        origins=(ori_lat, ori_lng),
        destinations=(dest_lat, dest_lng),
        mode='bicycling'
    )
    return distance['rows'][0]['elements'][0]['distance']['text']

@lru_cache
def get_travel_time_by_mode(ori_lat, ori_lng, dest_lat, dest_lng, mode):
    if mode == 'b':
        mode = 'bicycling'
    elif mode == 'd':
        mode = 'driving'

    distance = maps_client.distance_matrix(
        origins=(ori_lat, ori_lng),
        destinations=(dest_lat, dest_lng),
        mode=mode,
    )
    return distance['rows'][0]['elements'][0]['duration']['text']

@lru_cache
def estimate_co2_saved(ori_lat, ori_lng, dest_lat, dest_lng):
    bike_distance = get_distance_by_mode(ori_lat, ori_lng, dest_lat, dest_lng, 'b')
    driving_distance = get_distance_by_mode(ori_lat, ori_lng, dest_lat, dest_lng, 'd')

    bike_data = bike_distance.split(' ')
    driving_data = driving_distance.split(' ')

    # distances measured in km
    bike_distance = float(bike_data[0])
    # adjust for short rides
    if bike_data[1] == 'm':
        bike_distance /= 1000
    
    # emissions estimated in kg (0.021 kg/km)
    bike_emissions = bike_distance * 0.021

    driving_distance = float(driving_data[0])
    if driving_data[1] == 'm':
        driving_distance /= 1000
    
    # emissions estimated in kg (0.192 kg/km)
    driving_emissions = driving_distance * 0.192

    return driving_emissions - bike_emissions

@lru_cache
def estimate_delta_time(ori_lat, ori_lng, dest_lat, dest_lng):
    est_bike_time = get_travel_time_by_mode(ori_lat, ori_lng, dest_lat, dest_lng, 'b')
    driving_time = get_travel_time_by_mode(ori_lat, ori_lng, dest_lat, dest_lng, 'd')

    bike_data = est_bike_time.split(' ')
    driving_data = driving_time.split(' ')

    # time measured in minutes
    if bike_data[1] == 'hour':
        est_bike_time = int(bike_data[0]) * 60 + int(bike_data[2])
    else:
        est_bike_time = int(bike_data[0])

    if driving_data[1] == 'hour':
        driving_time = int(driving_data[0]) * 60 + int(driving_data[2])
    else:
        driving_time = int(driving_data[0])

    return {'bike': est_bike_time, 'drive': driving_time}

# print(estimate_co2_saved(40.746153593,-73.916188598,40.67308,-73.94191))
# print(estimate_delta_time(40.746153593,-73.916188598,40.67308,-73.94191))

@lru_cache
def estimate_lat_lng_to_km(ori_lat, ori_lng, dest_lat, dest_lng):
    # units in km
    radius = 6371

    dlat = math.radians(dest_lat - ori_lat)
    dlon = math.radians(dest_lng - ori_lng)

    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(ori_lat)) * math.cos(math.radians(dest_lat)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radius * c

def is_trip_possible(ori_lat, ori_lng, dest_lat, dest_lng, start_time: datetime.datetime, end_time: datetime.datetime):
    est_distance = estimate_lat_lng_to_km(ori_lat, ori_lng, dest_lat, dest_lng)
    time_elapsed = (end_time - start_time).total_seconds() / 3600

    # fastest reasonable biking speed in the city is 20 km/h
    return est_distance / 20 <= time_elapsed

# def compute_station_matrix():
#     # pd.read_csv('distance_matrix.csv', delimiter=',')

#     station_df = get_stations_df()

#     station_matrix = {}
#     for _, row in station_df.iterrows():
#         station_matrix[row['station_id']] = (row['lat'], row['lon'])
#     # return station_matrix
        
#     distance_matrix = pd.DataFrame()
#     data = {}
#     indices = []
#     for (ori_id, (lat, lon)) in station_matrix.items():
#         for (dest_id, (dest_lat, dest_lng)) in station_matrix.items():
#             if dest_id not in data:
#                 data[dest_id] = []
#             distance = 1.5 * get_lat_lng_to_km(lat, lon, dest_lat, dest_lng)

#             # distance_matrix.at[ori_id, dest_id] = distance
#             data[dest_id].append(distance)
        
#         indices.append(ori_id)
#         # break
    
#     distance_matrix = pd.Dataframe(data, index=indices)
            
#     distance_matrix.to_csv('distance_matrix.csv', sep=',', index=False)


if __name__ == '__main__':
    pass

