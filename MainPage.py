import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from distance import estimate_co2_saved, estimate_delta_time

# RUN APP COMMAND - python3 -m streamlit run MainPage.py
st.set_page_config(
    page_title="Point 72 Competition App",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

NUM_TO_MONTH = {1: 'January',2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
FEED_LENGTH = 30
GOAL_CO2 = 1260783
START_CO2 = 178171.3
refresh_tick_count = st_autorefresh(interval=30000, limit=100)

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
    feed_df = df[df['ended_at'] <= curr_timestamp]
    feed_df = feed_df.sort_values(by='ended_at').tail(n)

    return feed_df
selected_date = datetime(2024, 3, 5, 9, 8, 26) + timedelta(hours=refresh_tick_count)
df = get_heatmap('./data/202403-citibike-tripdata_1.csv', selected_date)

#Estimate the amount of CO2 currently emitted this month
total_seconds = 31 * 24 * 60 * 60
current_timestamp = (selected_date - datetime(selected_date.year, selected_date.month, 1)).total_seconds()
percentage = current_timestamp / total_seconds

# Get the feed information
feed_df = get_feed_data(df, FEED_LENGTH, selected_date)
amt_of_CO2_saved = []
bike_car_commute_times = []
for i, row in feed_df.iterrows():
    ori_lat, ori_lng, dest_lat, dest_lng = row['start_lat'], row['start_lng'], row['end_lat'], row['end_lng']
    amt_of_CO2_saved.append(estimate_co2_saved(ori_lat, ori_lng, dest_lat, dest_lng))
    bike_car_commute_times.append(estimate_delta_time(ori_lat, ori_lng, dest_lat, dest_lng))

#Get live csp data from txt file
with open('./co2_saved.txt', 'r') as file:
    # Read the first line of the file into a string
    co2_30_sec_total = float(file.readline())
    co2_saved_total_live = float(file.readline())

# UI BELOW

## Dashboard Design
col = st.columns((2.5, 4, 2), gap='large')
with col[0]:
    st.write('### 🚲 Live Heatmap of People Using CitiBike')
    st.write('#### Time:', selected_date)
    st.plotly_chart(get_nyc_heatmap(df))
with col[1]:
    with st.container():
        st.markdown("""
                    # NYC Amount of CO₂ Saved
                    """)
        st.progress(percentage, text="For the Month of " + NUM_TO_MONTH[selected_date.month] +  " 2024")
        st.write("🍃 Total Amount of CO₂ saved: *" + str(round(START_CO2 + co2_saved_total_live, 1)) + "* kilograms (**" + str(round(percentage * 100, 1)) + "%** of the way there!)")
        st.write("🎯 Goal Amount of CO₂ to save this month: *" + str(GOAL_CO2) + "* kilograms")
    st.write("## 🏢 Live Feed of Manhattan CitiBikers")
    with st.container(height=420, border=True):
        # REPLACE WITH CSP DATA
        if float(co2_30_sec_total) != 0.0:
            with st.container(border=True):
                    co2_num = round(float(co2_saved_total_live), 3)
                    st.markdown("🌆 The city of Manhattan just saved :green[**" + str(co2_30_sec_total) + " kg of CO₂**] in the past 30 seconds!")
                    st.markdown('<div style="text-align: right;">+🍃: ' + str(co2_30_sec_total) + ' kg of CO₂', unsafe_allow_html=True)
        for i in range(FEED_LENGTH):
            with st.container(border=True):
                st.markdown("👤 *Anonymous* just rode for " + str(bike_car_commute_times[i]['bike']) + " minutes, saving :green[**" + str(round(amt_of_CO2_saved[i], 3)) + " kg of CO₂**]:")
                st.markdown('<div style="text-align: right;">+🍃: ' + str(round(amt_of_CO2_saved[i], 3)) + ' kg of CO₂, saved ' + str(bike_car_commute_times[i]['drive'] - bike_car_commute_times[i]['bike']) + ' min compared to car</div>', unsafe_allow_html=True)
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
                - 🍃 CO2: 7.12 kg
                - 🕒 Time saved: 16 minutes
                 
                **All time, you've saved...**
                - 🍃 CO2: 53.4 kg
                - 🕒 Time saved: 109 minutes
                 """)
        st.write("You are in the :red[**95th percentile**]: of CitiBike users for being environmently friendly this month!")

