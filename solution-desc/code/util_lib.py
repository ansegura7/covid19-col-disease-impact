# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.2.0
    Created on: Sep 22, 2020
    Updated on: Sep 23, 2020
    Description: Library with utility functions
"""

# Import Python
import os
import json
import yaml
import numpy as np
import pandas as pd
from math import sqrt, log
from scipy import stats
from sklearn.metrics import mean_squared_error

############################
### Start Util Functions ###
############################

# Util function - Calculate the percentage error
def percentage_error(actual, predicted):
    res = np.empty(actual.shape)
    for j in range(actual.shape[0]):
        if actual[j] != 0:
            res[j] = (actual[j] - predicted[j]) / actual[j]
        else:
            res[j] = predicted[j] / np.mean(actual)
    return res

# Util function - Calculate root mean squared error or RMSE
def calc_rmse(actual, predicted):
    return sqrt(mean_squared_error(actual, predicted))

# Util function - Calculate mean absolute percentage error or MAPE
def calc_mape(y_true, y_pred): 
    return np.mean(np.abs(percentage_error(np.asarray(y_true), np.asarray(y_pred)))) * 100

# Util function - Calculate AIC for regression
def calc_aic(actual, predicted, k=1):
    n = len(actual)
    mse = mean_squared_error(actual, predicted)
    aic = n * log(mse) + 2 * k
    return aic

# Util function - Calculate BIC for regression
def calc_bic(actual, predicted, k=1):
    n = len(actual)
    mse = mean_squared_error(actual, predicted)
    bic = n * log(mse) + k * log(n)
    return bic

# Util function - Calculate confidence interval
def get_interval(y, y_pred, pi=0.99):
    n = len(y)
    
    # Get standard deviation of y_test
    sum_errs = np.sum((y - y_pred)**2) / (n - 2)
    stdev = np.sqrt(sum_errs)
    
    # Get interval from standard deviation
    one_minus_pi = 1 - pi
    ppf_lookup = 1 - (one_minus_pi / 2)
    z_score = stats.norm.ppf(ppf_lookup)
    interval = z_score * stdev
    
    return interval

# Util function - Tracking signal monitors any forecasts
def tracking_signal(y_truth, y_forecasted, ci_tolerance):
    ts_period = 0
    ts_total = 0
    n = len(y_truth)
    
    if n > 0 :
        cv = 0
        ce = 0
        
        # Tracking signal calculation
        for i in range(n):
            v = abs(y_truth[i] - y_forecasted[i])
            cv += v
            dma = cv / (i + 1)
            e = y_truth[i] - y_forecasted[i]
            ce += e
            ts = ce / dma
            
            # Counters
            if ts <= ci_tolerance:
                ts_total += 1
                
            elif ts_period == 0:
                ts_period = i
        
        # Calculate total valid periods
        if ts_total == n:
            ts_total = 1.0
            ts_period = n
        else:
            ts_total = round(ts_total / n, 4)
        
    return ts_period, ts_total

# Util function - Read dict from JSON file
def get_dict_from_json(json_path):
    result = dict()
    
    with open(json_path) as f:
        result = json.load(f)
    
    return result

# Util function - Read dict from YAML file
def get_dict_from_yaml(yaml_path):
    result = dict()
    
    with open(yaml_path) as f:
        yaml_file = f.read()
        result = yaml.load(yaml_file, Loader=yaml.FullLoader)
    
    return result

# Util function - Create a directory if it does not exist
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# Util function - Save dataframe to CSV file 
def save_df_to_csv_file(filename, df, index=True):
    result = ''
    try:
        if os.path.exists(filename):
            # Append mode without header
            df.to_csv(filename, index=index, mode='a', header=False)
        else:
            # Write mode with header (only first time)
            df.to_csv(filename, index=index, mode='w', header=True)
        
    except Exception as e:
        result = ' - Error: ' + str(e)
    return result

# Util function - Check if column exists in df from a list of columns
def df_columns_exists(df, column_list):
    result = False
    
    if df is not None and len(column_list):
        result = True
        for col in column_list:
            if col not in df.columns:
                return False
    
    return result

# Util function - Concat 2 dataframes, which is outer join by default
def merge_data(df1, df2, index):
    df = pd.DataFrame()
    
    if df_columns_exists(df1, index) and df_columns_exists(df2, index):
        df1 = df1.set_index(index)
        df2 = df2.set_index(index)
        df = pd.concat([df1, df2], axis=1)
    
    return df

##########################
### End Util Functions ###
##########################
