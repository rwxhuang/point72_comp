import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# RUN APP COMMAND - python3 -m streamlit run MainPage.py
TRANSPORTATIONS = ['CitiBikes', 'MTA']

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

def get_nyc_heatmap(df, selected_date):
    df = df[(df['started_at'] >= selected_date) & (df['ended_at'] >= selected_date)]
    station_counts = df.groupby('start_station_id').size()
    df = df.drop_duplicates(subset='start_station_id')
    df['freq'] = station_counts.values
    fig = px.density_mapbox(df, lat='start_lat', lon='start_lng', z='freq', radius=8,
                            center=dict(lat=40.757, lon=-73.92319), zoom=9,
                            mapbox_style="open-street-map")
    fig.update_layout(width=425, height=600)
    return fig

def get_feed_data(df, n, curr_timestamp):
    feed_df = df[df('ended_at') <= curr_timestamp]
    feed_df = feed_df.sort_values(by='ended_at').tail(n)

    return feed_df

# def download_and_process_data(csv_file):
#     df = pd.read_csv(csv_file, delimiter=',')

#     df = df[['started_at', 'ended_at', 'start_station_id', 'end_station_id', 'start_lat', 'start_lng', 'end_lat', 'end_lng']]

#     df['started_at'] = pd.to_datetime(df['started_at']).dt.round('H')
#     df['ended_at'] = pd.to_datetime(df['ended_at']).dt.round('H')

#     df['start_station_id'] = df['start_station_id'].astype(str)
#     df['end_station_id'] = df['end_station_id'].astype(str)

#     df = df[(df['start_station_id'] != 'nan') & (df['end_station_id'] != 'nan')]

#     df = df.dropna()

#     return df

def groupby_time_location_processing(df):
    df_start = df.groupby(['start_station_id', 'started_at']).first().reset_index('start_station_id').reset_index('started_at')
    df_start_size = df.groupby(['start_station_id', 'started_at']).size().reset_index('start_station_id').reset_index('started_at')

    df_start['size'] = df_start_size[0]

    return df_start

# UI BELOW
st.set_page_config(
    page_title="Point 72 Competition App",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

## Dashboard Design
col = st.columns((2.5, 4, 2), gap='large')
with col[0]:
    st.header('🚲 Live Heatmap of People Using CitiBike')
    df = get_df()
    start_date = df['started_at'].min().to_pydatetime()
    end_date = df['ended_at'].max().to_pydatetime()
    selected_date = st.slider(
        "Select a date range",
        min_value=start_date,
        max_value=end_date,
        value=start_date,
        step=timedelta(minutes=1),
    )
    st.plotly_chart(get_nyc_heatmap(df, selected_date))
with col[1]:
    with st.container():
        st.markdown("""
                    # NYC Amount of CO2 Saved
                    """)
        st.progress(40, text="For the Month of March 2024")
        st.write("🍃 Total Amount of CO2 saved: 56,000,000 kilograms")
    with st.container(border=True):
        st.write("## 🏢 Live Feed of Manhattan CitiBikers")
        for i in range(6):
            with st.container(border=True):
                st.markdown("""
                            👤 Anonymous just rode for **15 minutes**, saving :green[**60 gallons of CO2**]:
                            """)
                st.markdown('<div style="text-align: right;">+🍃: 60 kg of CO2</div>', unsafe_allow_html=True)
with col[2]:
    with st.container():
        st.write('''
        ### About the application         
        Track live the usage of CitiBikes as the community of NYC attempts to reduce CO2 emissions together.
        - :orange[**Implementers**]: Roderick Huang, Shepard Jiang, Arnold Su
        - :orange[**Dataset**]: Live feed from [CitiBike System Data](https://citibikenyc.com/system-data)
        ''')
    with st.container(border=True):
        st.write("## 🧍 What is your contribution?")

