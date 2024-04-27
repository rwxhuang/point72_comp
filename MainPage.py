import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# RUN APP COMMAND - python3 -m streamlit run MainPage.py
st.set_page_config(
    page_title="Point 72 Competition App",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

NUM_TO_MONTH = {1: 'January',2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
FEED_LENGTH = 30
refresh_tick_count = st_autorefresh(interval=10000, limit=10)

def get_nyc_heatmap(df):
    fig = px.density_mapbox(df, lat='start_lat', lon='start_lng', z='riders', radius=8,
                            center=dict(lat=40.75651, lon=-73.98319), zoom=11,
                            mapbox_style="carto-positron")
    fig.update_layout(width=425, height=600)
    return fig

def get_heatmap(csv_file, curr_timestamp):
    df = pd.read_csv(csv_file, delimiter=',')

    df = df[['started_at', 'ended_at', 'start_station_id', 'end_station_id', 'start_lat', 'start_lng', 'end_lat', 'end_lng']]

    df['started_at'] = pd.to_datetime(df['started_at']) #dt.round('H')
    df['ended_at'] = pd.to_datetime(df['ended_at']) #dt.round('H')

    df['start_station_id'] = df['start_station_id'].astype(str)
    df['end_station_id'] = df['end_station_id'].astype(str)

    df = df[(df['start_station_id'] != 'nan') & (df['end_station_id'] != 'nan')]

    df = df.dropna()

    cutoff_timestamp = curr_timestamp - timedelta(hours=1)
    df = df[(df['started_at'] >= cutoff_timestamp) & (df['started_at'] <= curr_timestamp)]

    df_heat = df.groupby(['start_station_id']).first().reset_index('start_station_id')
    df_heat['riders'] = df.groupby(['start_station_id']).size().reset_index('start_station_id')[0]

    return df_heat

def get_feed_data(df, n, curr_timestamp):
    feed_df = df[df('ended_at') <= curr_timestamp]
    feed_df = feed_df.sort_values(by='ended_at').tail(n)

    return feed_df

# def download_and_process_data(csv_file):
#     df = pd.read_csv(csv_file, delimiter=',')

    return df_heat

# UI BELOW

## Dashboard Design
col = st.columns((2.5, 4, 2), gap='large')
with col[0]:
    st.write('### 🚲 Live Heatmap of People Using CitiBike')
    selected_date = datetime(2024, 3, 5, 9, 1, 0) + timedelta(hours=refresh_tick_count)
    st.write('#### Time:', selected_date)
    df = get_heatmap('./data/202403-citibike-tripdata_1.csv', selected_date)
    st.plotly_chart(get_nyc_heatmap(df))
with col[1]:
    with st.container():
        st.markdown("""
                    # NYC Amount of CO2 Saved
                    """)
        st.progress(40, text="For the Month of " + NUM_TO_MONTH[selected_date.month] +  " 2024")
        st.write("🍃 Total Amount of CO2 saved: " + " kilograms")
        st.write("🎯 Goal Amount of CO2 to save: " + " kilograms")
    st.write("## 🏢 Live Feed of Manhattan CitiBikers")
    with st.container(height=420, border=True):
        for i in range(6):
            with st.container(border=True):
                st.markdown("""
                            👤 *Anonymous* just rode for **15 minutes**, saving :green[**60 gallons of CO2**]:
                            """)
                st.markdown('<div style="text-align: right;">+🍃: 60 kg of CO2, saved 5 min compared to car</div>', unsafe_allow_html=True)
with col[2]:
    with st.container():
        st.write('''
        ### About the application         
        Track live the usage of CitiBikes as the community of NYC attempts to reduce CO2 emissions together.
        - :orange[**Implementers**]: Roderick Huang, Shepard Jiang, Arnold Su
        - :orange[**Dataset**]: Live feed from [CitiBike System Data](https://citibikenyc.com/system-data)
        - :orange[**Calculations**]: [Google Maps Platform](https://developers.google.com/maps)
        ''')
    with st.container(height=410, border=True):
        st.write("### 🧍 Your contribution")
        st.write("""
                **This month, you've saved...**
                - 🍃 CO2: 5000 kg
                - 🕒 Time saved: 15 minutes
                 
                **All time, you've saved...**
                - 🍃 CO2: 5000 kg
                - 🕒 Time saved: 15 minutes
                 """)
        st.write("You are in the :red[**95th percentile**]: of CitiBike users for being environmently friendly!")

