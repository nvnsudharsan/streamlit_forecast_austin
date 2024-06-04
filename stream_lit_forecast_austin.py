#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 18:18:42 2024

@author: geo-ns36752
"""

import streamlit as st
import xarray as xr
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import requests
from io import BytesIO


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

# Load data using xarray
@st.cache_data 
def ECMWF_forecast(lat = 30.2672, lon = -97.7431):
    url = 'https://github.com/nvnsudharsan/streamlit_forecast_austin/raw/main/forecast_ecmwf_may_.nc'
    local_filename = 'forecast_ecmwf_may_.nc'
    # Download the file
    download_file(url, local_filename)
    data = xr.open_dataset(local_filename, engine='netcdf4')
    t2m = data.t2m
    t2m = t2m - 273.15
    t2m = (t2m*(9/5))+32
    temp_austin = t2m.sel(latitude=lat, method='nearest').sel(longitude=lon, method='nearest')
    tmax_austin = temp_austin.resample(time='1D').max()
    time = tmax_austin.time.values
    median_temp = tmax_austin.median('number').values
    min_temp = tmax_austin.min('number').values
    max_temp = tmax_austin.max('number').values
    return time, median_temp, min_temp, max_temp

def ECMWF_anom(month):
    url             = 'https://github.com/nvnsudharsan/streamlit_forecast_austin/raw/main/type_fcmean.nc'
    local_filename  = 'type_fcmean.nc'
    download_file(url, local_filename)
    anom_fc         = xr.open_dataset(local_filename,engine='netcdf4')
    anom_fc         = anom_fc.t2a
    anom_fc_median  = anom_fc.median('number')
    temp_anom       = anom_fc_median[month,:,:].values
    lat             = anom_fc.latitude.values
    lon             = anom_fc.longitude.values
    return temp_anom, lat, lon

def main():
    st.title("Temperature prediction for Austin - ECMWF")
    st.write('The model is initiated on May 1st')

    # File uploader for NetCDF files
   # uploaded_file = st.file_uploader("Upload a NetCDF file", type=["nc"])

   # if uploaded_file is not None:
        # Load data using xarray
    time, median_temp, min_temp, max_temp = ECMWF_forecast(30.2672,-97.7431)

    # Display ECMWF Forecast
    #st.write("Forecast for Austin")
    fig = go.Figure(data=go.Scatter(x=time, y=median_temp, mode='lines', line=dict(width=4,color='red'), name = 'Median'))
    fig.add_trace(go.Scatter(
            x=time,
            y=min_temp,
            mode='lines',
            name='Minimum',
            line=dict(color='grey',width=2.5)
            ))
    fig.add_trace(go.Scatter(
            x=time,
            y=max_temp,
            mode='lines',
            fill='tonexty',
            name='Maximum',
            line=dict(color='grey',width=2.5)
            ))
    fig.update_traces(opacity=0.8)
    fig.update_layout(title='Temperature prediction for Austin (ECMWF)', xaxis_title='Time', yaxis_title='Temperature (°F)')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='white')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='white')
    st.plotly_chart(fig)
    st.write('The daily maximum temperature from 51 members in the model are used here. This shows the trend of daily maximum temperature in Austin.')

    st.write("<h2>Temperature Anomaly over Texas<h2>", unsafe_allow_html=True)
    option_mapping = {"May": 0, "June": 1, "July": 2, "August":3}
    selected_option = st.selectbox("Select a month", list(option_mapping.keys()))
    selected_value = option_mapping[selected_option]
    temp_anom, lat, lon = ECMWF_anom(selected_value)
    fig, ax = plt.subplots(nrows=1,ncols=1,
                        subplot_kw={'projection': ccrs.PlateCarree()},
                        figsize=(12,8))
    temp_anom_fc_f = (temp_anom*(9/5))
    im = plt.pcolormesh(lon,lat,temp_anom_fc_f,cmap='RdBu_r',vmax =4, vmin=-4)
    cb = plt.colorbar(im)
    cb.set_label('Temperature Anomaly (°F)',size=15)
    ax.set_extent([-107, -93, 25, 37])
    ax.add_feature(cfeature.STATES, facecolor='none')
    ax.plot(-97.7431, 30.2672, marker='o', color='darkgreen', transform=ccrs.PlateCarree(),markersize = 10)
    ax.text(-98.35, 29.75,'Austin',fontsize=15)
    ax.set_xticks(np.arange(-107,-92,2), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(25,38,2), crs=ccrs.PlateCarree())
    ax.set_ylabel('Latitude', size = 15)
    ax.set_xlabel('Longitude', size = 15)
    st.pyplot(fig)
    st.write('The figure shows the temperature anomaly for each summer month')
        
if __name__ == "__main__":
    main()
