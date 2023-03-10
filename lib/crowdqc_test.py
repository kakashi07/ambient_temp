"""
Created on Feb 7

@author: Gaurav
@version: 1.0

Implementation of CrowdQC quality checks.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
pd.options.mode.chained_assignment = None  # default='warn'


def level_check(dataframe, temp_field,time_field):
    ''' This function simply checks if valid columns are present or not'''
    
        
    assert temp_field in dataframe.columns , "Temp column doesn't exist in dataframe"
    assert len(dataframe[temp_field])>0 , "Empty dataframe given"
    assert time_field in dataframe.columns , f"Invalid Time column : {time_field}"
    
    print('Level 0 check passed : Valid fields present')
    
    return True

def level1_check(dataframe,temp_field):
    ''' '''
    
    if max(dataframe[temp_field]) > 60 or min(dataframe[temp_field]) < -40:
        print('QC check 1 failed : Temperature exceeds given range')
        print('#########################')
        print(max(dataframe[temp_field]))
        print(min(dataframe[temp_field]))        
        
    else:
        print('QC check 1 passed : Gross Error Test')
        print('#########################')
        
        
    return 

def level2_check(dataset,temp_field,time_field):
    # This measures spatial consistency L2 
#     print(dataset.head())

    time1 = dataset.iloc[0][time_field]
    time2 = dataset.iloc[1][time_field]

    time3 = dataset.iloc[len(dataset)//2][time_field]
    time4 = dataset.iloc[len(dataset)//2 + 1][time_field]

    time5 = dataset.iloc[len(dataset)-2][time_field]
    time6 = dataset.iloc[len(dataset)-1][time_field]

    delta1 = ((datetime.strptime(str(time2), "%Y-%m-%d %H:%M:%S") - datetime.strptime(str(time1), "%Y-%m-%d %H:%M:%S")).seconds)/60
    delta2 = ((datetime.strptime(str(time4), "%Y-%m-%d %H:%M:%S") - datetime.strptime(str(time3), "%Y-%m-%d %H:%M:%S")).seconds)/60
    delta3 = ((datetime.strptime(str(time6), "%Y-%m-%d %H:%M:%S") - datetime.strptime(str(time5), "%Y-%m-%d %H:%M:%S")).seconds)/60
    if delta1==delta2==delta3:
#         print('All time ranges equal')
        print("")

    else:
        print("Time ranges not equal, taking average for QC2 check")

    avg = np.average([delta1,delta2,delta3])
#     print(avg)
    
    # if 'key' in dataset.columns: 
    #     station_key = 'key'
    # else:
    #     station_key = 'station'

    station_key = 'station'
    
    stations = dataset[station_key].unique()
    invalids = []
    for station in stations:
        dataset_cpy = dataset[dataset[station_key]==station]
        
        differences = dataset_cpy[temp_field].diff()[1:]

        if avg <= 5:
            invalid_ = differences[differences > 6]
            time_resolution = 5
        if avg >  5 and avg <= 15:
            invalid_ = differences[differences > 10]
            time_resolution = 15        
        if avg >  15 and avg <= 30:
            invalid_ = differences[differences > 15]
            time_resolution = 30        
        if avg >  30 and avg <= 60:
            invalid_ = differences[differences > 20]
            time_resolution = 60        

        if avg > 60:
            print("Temporal resolution is greater than 1 hour")
            time_resolution = 1000
        
        invalids.append(invalid_)
    if len(invalid_) > 0:
        print(f"QC Check 2 failed : Temporal inconsistency found, {avg} minutes range , for {len(invalid_)} rows  ")
        print('#########################')

    if len(invalid_) == 0:
        print("QC Check 2 passed : Spike Test")
        print('#########################')
    
    return time_resolution
        
#     return differences
        
#     print(invalid_)

def level3_check(dataset,temp_field,resolution):
    ''' This function tests for temporal persistance'''
    #need to manually test this function
    if 'key' in dataset.columns: 
        station_key = 'key'
    else:
        station_key = 'station'
        
    stations = dataset[station_key].unique()
    fi_list = []
    for station in stations:
        dataset_cpy = dataset[dataset[station_key]==station]
        
        if resolution==5:
            rollings = 24
            dataset_cpy['rolling_mean'] = dataset_cpy[temp_field].iloc[::-1].rolling(rollings).mean().iloc[::-1]

        elif resolution==15:
            rollings = 36
            dataset_cpy['rolling_mean'] = dataset_cpy[temp_field].iloc[::-1].rolling(rollings).mean().iloc[::-1]

        elif resolution==30:
            rollings = 54
            dataset_cpy['rolling_mean'] = dataset_cpy[temp_field].iloc[::-1].rolling(rollings).mean().iloc[::-1]

        elif resolution==60:
            rollings = 72
            dataset_cpy['rolling_mean'] = dataset_cpy[temp_field].iloc[::-1].rolling(rollings).mean().iloc[::-1]

        else:
            print("Invalid Time resolution")


        failed_indexes = dataset_cpy[dataset_cpy.rolling_mean == dataset_cpy[temp_field]].index
        fi_list.append(failed_indexes)
        
        if len(failed_indexes)>0:
            print(f"QC Check 3 failed : {len(failed_indexes)} rows for {station}")
            print(f"\t Failed indexes : {failed_indexes}")
            

        else:
            print("QC Check 3 passed : Spike Test")
              

def outlier_check(dataframe, temp_field = 'temp',time_field = 'expire_time_gmt'):

    '''Parent wrapper that completes the l1, l2, l3 QC check controls from CrowdQC paper
    key : data_source {wunder, netatmos, lter}
    time_field : column to be used as time
    '''
    
    l0_status = level_check(dataframe,temp_field,time_field)
    
    if l0_status:
        #converting temperature to C for wunderground data
        if temp_field=='temp':
            dataframe['temp'] = (dataframe['temp'] - 32) * (5/9)
        
        level1_check(dataframe,temp_field)
        resolution = level2_check(dataframe,temp_field,time_field)
        level3_check(dataframe,temp_field,resolution)
        

#todo: what to do with incomplete station data
def level4_check():
    
    return
