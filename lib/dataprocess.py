import os
import pandas as pd
import numpy as np

import plotly.express as pe
import plotly.offline as pyo
from datetime import datetime

pyo.init_notebook_mode()

def combine_dataframes(dframes):
    df = pd.concat(dframes,ignore_index=True)
    df = df.reset_index(drop=True).iloc[:,1:]
    df.drop_duplicates(subset=['key','expire_time_gmt','valid_time_gmt','temp','dewPt'])
    
    return df

def aggregation(df):
    #aggregation of metrics on hourly basis
    df['beg_time'] = pd.to_datetime(df.beg_time)
    df.index = [df.beg_time,df.station]
    df = df.groupby([pd.Grouper(level='station'),pd.Grouper(level='beg_time',freq='H')]).mean()
    
    #resetting the index for daily animations
    #dfx = df.copy()        #Avoiding this to save memory
    df = df.reset_index()
    df['beg_time'] = pd.to_datetime(df.beg_time)
    df['yday'] = df['beg_time'].apply(lambda x : datetime.timetuple(x).tm_yday)
    
    return df

def process_netatmos(df):
    df = df.drop([df.columns[0]],axis = 1)
    df = df.groupby("latitude", group_keys=True).apply(lambda x: x)

    #todo : Find a better way to do this ==> df.map()
    df_cpy = df.copy()
    df_cpy['station'] = df_cpy['latitude']
    df_cpy['station'] = df_cpy['station'].apply(lambda x : 'Station_1' if x== 43.06395 else x)
    df_cpy['station'] = df_cpy['station'].apply(lambda x : 'Station_2' if x== 43.0704332 else x)
    df_cpy['station'] = df_cpy['station'].apply(lambda x : 'Station_3' if x== 43.073576 else x)
    df_cpy['station'] = df_cpy['station'].apply(lambda x : 'Station_4' if x== 43.0924018 else x)
    df_cpy['station'] = df_cpy['station'].apply(lambda x : 'Station_5' if x== 43.0958646 else x)
    df_cpy['station'] = df_cpy['station'].apply(lambda x : 'Station_6' if x== 43.1107383 else x)
    df_cpy['station'] = df_cpy['station'].apply(lambda x : 'Station_7' if x== 43.127702907735 else x)
    
    df_cpy = aggregation(df_cpy)
    
    return df_cpy

def process_lter(lter_combined):
    lter_combined.columns = [x.lower() for x in lter_combined.columns]
    lter_combined['sample_time'] = lter_combined['sample_time'].apply(lambda x: str(x).zfill(4))
    lter_combined['sample_time'] = lter_combined['sample_time'].apply(lambda x: str(x)[:2]+':'+str(x)[2:]+':00')
    lter_combined['beg_time'] = lter_combined.sample_date.str.cat(lter_combined.sample_time, sep=' ')


    lter_combined['beg_time'] = pd.to_datetime(lter_combined.beg_time)
    lter_combined.index = [lter_combined.beg_time,lter_combined.sid]
    lter_combined = lter_combined.groupby([pd.Grouper(level='sid'),pd.Grouper(level='beg_time',freq='H')]).mean()


    lter_combined = lter_combined.reset_index()
    lter_combined['beg_time'] = pd.to_datetime(lter_combined.beg_time)
    lter_combined['yday'] = lter_combined['beg_time'].apply(lambda x : datetime.timetuple(x).tm_yday)
    lter_combined['value'] = (lter_combined['value']-32)*(5/9)

    lter_combined.columns = ['station', 'beg_time', 'temperature', 'latitude', 'longitude', 'yday']

    return lter_combined

def process_wunder(pws_df):
    pws_df['beg_time'] = pd.to_datetime(pws_df.obsTimeLocal)
    pws_df = pws_df.rename({"stationID":"station","lat":"latitude","lon":"longitude"},axis=1)
    
    pws_df = pws_df.sort_values(by=['station','beg_time'])
    pws_df.index = [pws_df.beg_time,pws_df.station]
    pws_df = pws_df.groupby([pd.Grouper(level='station'),pd.Grouper(level='beg_time',freq='H')]).mean()

    #resetting the index for daily animations
    #pws_dfx = pws_df.copy()        #Avoiding this to save memory
    pws_df = pws_df.reset_index()
    pws_df['beg_time'] = pd.to_datetime(pws_df.beg_time)
    pws_df['yday'] = pws_df['beg_time'].apply(lambda x : datetime.timetuple(x).tm_yday)

    pws_df.sort_values(by = ['station','beg_time','yday'],inplace=True)

    return pws_df

def plot_(dfx,animation_frame_comp,frame_duration):
    '''
    animation_frame_comp : defines which column to animate upon (eg. year, month)
    frame_duration : defines how fast the animation should be
    '''
    
    fig = pe.scatter_mapbox(dfx,lat='latitude',lon = 'longitude',animation_frame='yday',color = 'temperature',range_color=[-30,30],hover_data=['station'],height = 610)

    fig.update_layout(mapbox_style = 'open-street-map',)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(marker=dict(size=14,color='black'))
    # fig.update_layouta(updatemenus=dict())

    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 100


    fig.show()