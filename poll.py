import csp
from csp import ts
from datetime import timedelta
from csp_bike import get_station_status

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
    
@csp.graph
def my_capacity_calculator(interval: timedelta):
    stations_data = poll_data(interval=interval)
    system_capacity = calculate_total_system_capacity(stations_data)
    csp.print("Total system capacity", system_capacity)

csp.run(my_capacity_calculator, timedelta(seconds=5), realtime=True)

        