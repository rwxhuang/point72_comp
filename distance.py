import os
import googlemaps

maps_client = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])

# Get biking distance between two locations
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
