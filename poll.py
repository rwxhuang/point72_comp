import csp
from csp import ts
from datetime import timedelta
from csp_bike import get_station_status, get_stations
import distance
import datetime
import random

@csp.node
def poll_data(interval: timedelta) -> ts[[dict]]:
    with csp.alarms():
        # this line tells `csp` we will have an alarm
        # we will schedule the alarm in a later step
        a_poll = csp.alarm(bool)

    with csp.start():
        # poll immediately after starting
        # by passing timedelta(seconds=0)
        csp.schedule_alarm(a_poll, timedelta(), True)

    if csp.ticked(a_poll):
        # grab the data
        to_return = get_station_status()

        # schedule next poll in `interval`
        csp.schedule_alarm(a_poll, interval, True)
        return to_return

@csp.node
def calculate_total_system_capacity(stations: ts[[dict]]) -> ts[int]:
    with csp.state():
        # these are stateful variables that will retain their
        # value in between "ticks"
        s_capacity = 0
        s_stations = {}

    if csp.ticked(stations):
        # when a new list of stations "ticks", we'll do some
        # processing and emit a new "tick" as output
        for station in stations:
            # subtract prior capacity
            prior_capacity = s_stations.get(station["station_id"], {}).get("total_bikes_available", 0)
            s_capacity -= prior_capacity
    
            # now update our tracker and capacity
            s_stations[station["station_id"]] = station
            s_capacity += station["total_bikes_available"]
    
        # finally, "tick" out the result
        return s_capacity
    
@csp.node
def approximate_trips(stations: ts[[dict]]) -> ts[float]:
    with csp.state():
        # these are stateful variables that will retain their
        # value in between "ticks"
        station_data = get_stations()
        # print(station_data)

        # bikes currently in service, stored with time checked out and stationID
        s_bike_pool = set()

        # tabulate total CO2 saved
        s_co2_saved = 0

        # stations and their previous capacities, stored to track number of bikes checked out
        s_stations = {}

        init = True

    if csp.ticked(stations):
        # when a new list of stations "ticks", we'll do some
        # processing and emit a new "tick" as output

        for station in stations:
            # subtract prior capacity
            prior_capacity = s_stations.get(station["station_id"], {}).get("total_bikes_available", 0)
            current_capacity = station["total_bikes_available"]
            current_lat = station_data[station["station_id"]]["lat"]
            current_lon = station_data[station["station_id"]]["lon"]

            # if the station has less bikes than before, we assume they were checked out
            if current_capacity < prior_capacity:
                bikes_checked_out = prior_capacity - current_capacity

                s_bike_pool.add((station["station_id"], current_lat, current_lon, datetime.datetime.now() , bikes_checked_out))
            
            elif current_capacity > prior_capacity:
                current_time = datetime.datetime.now()

                bikes_returned = current_capacity - prior_capacity
            
                # bikes part of a possible trip
                potential_bikes = [bike_data for bike_data in s_bike_pool if 
                                     distance.is_trip_possible(bike_data[1], bike_data[2], current_lat, current_lon, bike_data[3], current_time)]
                


                for _ in range(bikes_returned):
                    if len(potential_bikes) == 0:
                        # average trip length: 12 minutes, 1.75 miles = 2.8 km
                        # car emissions - bike emissions
                        s_co2_saved += 2.8 * 0.192 - 2.8 * 0.021
                        continue

                    # otherwise randomly choose a possible bike for the trip
                    random_bike = random.choice(potential_bikes)
                    s_bike_pool.discard(random_bike)
                    if random_bike[4] > 1:
                        s_bike_pool.add((random_bike[0], random_bike[1], random_bike[2], current_time, random_bike[4] - 1))
                    
                    s_co2_saved += distance.estimate_co2_saved(random_bike[1], random_bike[2], current_lat, current_lon)

            # now update our tracker and capacity
            s_stations[station["station_id"]] = station

        if init:
            init = False
            s_co2_saved = 0

        print("bike pool: ", sum([bike[4] for bike in s_bike_pool]))

        with open("co2_saved.txt", "w") as f:
            f.write(str(s_co2_saved))
    
        # finally, "tick" out the result
        return s_co2_saved
    
@csp.graph
def my_capacity_calculator(interval: timedelta):
    stations_data = poll_data(interval=interval)
    # system_capacity = calculate_total_system_capacity(stations_data)
    # csp.print("Total system capacity", system_capacity)
    co2_saved = approximate_trips(stations_data)
    csp.print("Total CO2 saved", co2_saved)

csp.run(my_capacity_calculator, timedelta(seconds=15), realtime=True)

        