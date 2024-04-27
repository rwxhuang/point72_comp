import numpy as np
import pandas as pd
import datetime as dt

def get_df():
    df = pd.read_csv('./data/202403-citibike-tripdata_1.csv')
    df = df[['started_at', 'ended_at', 'start_station_id', 'end_station_id', 'start_lat', 'start_lng', 'end_lat', 'end_lng']]

    df['started_at'] = pd.to_datetime(df['started_at']).dt.round('H')
    df['ended_at'] = pd.to_datetime(df['ended_at']).dt.round('H')

    df['start_station_id'] = df['start_station_id'].astype(str)
    df['end_station_id'] = df['end_station_id'].astype(str)

    df = df[(df['start_station_id'] != 'nan') & (df['end_station_id'] != 'nan')]

    df = df.dropna()
    return df

def get_bike_df(df):
    ### IF ALREADY SAVED: JUST LOAD CSV BECAUSE THIS TAKES A LONG TIME

    df['start_time'] = df['started_at'].dt.round('min').dt.time
    df['end_time'] = df['ended_at'].dt.round('min').dt.time

    stations = df['start_station_id'].unique()
    df_bikes = {station: None for station in stations}
    for station in stations:
        df_station = df[(df['start_station_id'] == station) | (df['end_station_id'] == station)]
        df_station['net_change'] = df_station.apply(lambda x: -1 if x['start_station_id'] == station else 1, axis=1)
        df_station['timestamp'] = df_station.apply(lambda x: x['start_time'] if x['start_station_id'] == station else x['end_time'], axis=1)

        df_station = df_station.groupby('timestamp')['net_change'].mean().reset_index('timestamp')
        df_station.sort_values(by='timestamp')
        df_station['num_net_bikes'] = df_station['net_change'].cumsum()

        df_bikes[station] = df_station
    
    df_bike = pd.concat(df_bikes).reset_index().rename(columns={'level_0': 'station_id'})
    df_bike.to_csv('data/bike_net_change.csv')

    return df_bike

def graph_station(df_bike, station):
    df_bike[df_bike['station'] == station].plot(x='timestamp', y='num_net_bikes')