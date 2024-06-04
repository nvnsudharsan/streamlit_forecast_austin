#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 18:18:42 2024

@author: geo-ns36752
"""

import streamlit as st
import xarray as xr
import plotly.graph_objects as go

# Load data using xarray
@st.cache_data 
def ECMWF_forecast(lat = 30.2672, lon = -97.7431):
    data = xr.open_dataset('/Users/geo-ns36752/Downloads/forecast_ecmwf_may_.nc')
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

def ECMWF_

def main():
    st.title("Temperature Outlook for Austin")

    # File uploader for NetCDF files
   # uploaded_file = st.file_uploader("Upload a NetCDF file", type=["nc"])

   # if uploaded_file is not None:
        # Load data using xarray
    time, median_temp, min_temp, max_temp = ECMWF_forecast()

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
    fig.update_layout(title='Forecast for Austin (ECMWF)', xaxis_title='Time', yaxis_title='Temperature (°F)')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='white')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='white')
    st.plotly_chart(fig)
        
if __name__ == "__main__":
    main()
