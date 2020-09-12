# -*- coding: utf-8 -*-
"""
    Created By: Andres Segura Tinoco
    Created On: Sep 09, 2020
    Version: 1.0.0
    Description: Main class of the solution.
"""

# Import Python 
import os
import logging
import pandas as pd
import numpy as np
import scipy.stats as ss
import itertools
import timeit
from datetime import datetime
from math import sqrt, ceil, log
from warnings import filterwarnings

# Import Time Series libraries
import statsmodels.api as sm
from scipy import stats
from sklearn.metrics import mean_squared_error

######################
### UTIL FUNCTIONS ###
######################

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

# Util function - Tracking signal monitors any forecasts
def tracking_signal(y_truth, y_forecasted, ci_tolerance):
    ts_period = 0
    cv = 0
    ce = 0
    
    # Tracking signal calculation
    for i in range(len(y_truth)):
        v = abs(y_truth[i] - y_forecasted[i])
        cv += v
        dma = cv / (i + 1)
        e = y_truth[i] - y_forecasted[i]
        ce += e
        ts = ce / dma
        
        # Stop
        if ts >= ci_tolerance:
            ts_period = i + 1
            break
        
    return ts_period

# Util function - Group data by period
def group_data_by_period(data):
    
    # Grouping by epidemiological period
    gr_data = data.groupby(['year', 'period']).agg('sum')
    gr_data = gr_data.drop(columns=['month', 'week'])
    
    for ix, row in gr_data.iterrows():
        curr_date = min(data[(data['year'] == ix[0]) & (data['period'] == ix[1])]['date'])
        gr_data.at[ix, 'date'] = pd.to_datetime(curr_date).date()
    
    gr_data.reset_index(inplace=True)
    gr_data = gr_data.reindex(columns=['date', 'year', 'period', 'value'])
    gr_data = gr_data.set_index('date')    
    
    return gr_data

# Util function - Create a directory if it does not exist
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# Util function - Save dataframe to CSV file 
def save_df_to_csv_file(filename, df, index=True):
    try:
        df.to_csv(filename, index=index)
    except Exception as e:
        logging.error(' - Error: ' + str(e))

######################
### CORE FUNCTIONS ###
######################

# Core function - Read the CSV dataset and convert it to a dictionary by entity
def get_data_by_entity(filename):
    data_list = dict()
    
    # Read data from CSV dataset
    raw_data = pd.read_csv(filename, parse_dates=['date'])
    
    # Filter data by entity
    if len(raw_data):
        entity_list = raw_data['entity'].unique()
        
        # Filtering and grouping data by entity
        for entity in entity_list:
            entity_data = raw_data[raw_data['entity'] == entity]
            entity_data = group_data_by_period(entity_data)                
            data_list[entity] = entity_data
            
            # Save results
            filename = '../result/' + curr_disease.lower() + '/' + entity.lower() + '_aggr_data.csv'
            save_df_to_csv_file(filename, entity_data)
    
    return data_list

# Core function - Create a set of SARIMA configs to try
def arima_smoothing_configs(data_freq, max_param=3):
    
    # Define the p, d and q parameters to take any value between 0 and 2
    p = d = q = range(0, max_param)

    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p, d, q))

    # Generate all different combinations of seasonal p, q and q triplets
    seasonal_pdq  = [(x[0], x[1], x[2], data_freq) for x in list(itertools.product(p, d, q))]
    
    return pdq, seasonal_pdq

# Core function - Parameter selection for the ARIMA Time Series model
def arima_grid_search(series_data, perc_test):
    scores = []
    
    # Begin grid search
    start_time = timeit.default_timer()
    method = 'SARIMA'
    ci_tolerance = 3.0
    
    # Specify to ignore warning messages
    filterwarnings("ignore")
    
    # Start prediction from...
    ix_test = ceil(len(series_data) * (1 - perc_test))
    start_date = series_data.index[ix_test]
    
    # Calculation params
    data_freq = 13
    pdq, seasonal_pdq = arima_smoothing_configs(data_freq)
    
    # Grid search
    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                # Create and fit model
                model = sm.tsa.statespace.SARIMAX(series_data, order=param, seasonal_order=param_seasonal, 
                                                  enforce_stationarity=False, enforce_invertibility=False)
                model = model.fit()
                
                if model.aic > 0 or model.bic > 0:
                    
                    # Extract the predicted and true values of our time series
                    y_truth = series_data[start_date:]
                    
                    # Validate prediction One-step ahead Forecast
                    pred_basic = model.get_prediction(start=start_date, dynamic=False)
                    y_forecasted = np.array([max(round(p), 0) for p in pred_basic.predicted_mean])
                    
                    # Compute the errors 1
                    rmse = calc_rmse(y_truth, y_forecasted)
                    mape = calc_mape(y_truth, y_forecasted)
                    
                    # Validate prediction with Dynamic Forecast
                    pred_dynamic = model.get_prediction(start=start_date, dynamic=True, full_results=True)
                    y_forecasted = np.array([max(round(p), 0) for p in pred_dynamic.predicted_mean])
                    
                    # Compute the errors 2
                    rmse = (rmse + calc_rmse(y_truth, y_forecasted)) / 2
                    mape = (mape + calc_mape(y_truth, y_forecasted)) / 2
                    
                    # Compute variation coefficients
                    ts_var_coef = ss.variation(series_data.values)
                    pred_var_coef = ss.variation(y_forecasted)
                    
                    # Compute tracking signal for prediction
                    ts_period = tracking_signal(y_truth, y_forecasted, ci_tolerance)
                    
                    # Save result
                    scores.append( {'method': method, 'order': param, 'seasonal_order': param_seasonal,
                                    'ts_var_coef': round(ts_var_coef, 4), 'pred_var_coef': round(pred_var_coef, 4), 'tracking_signal': ts_period,
                                    'rmse': round(rmse, 4), 'mape': round(mape, 4), 'aic': round(model.aic, 4), 'bic': round(model.bic, 4)} )
                
            except Exception as e:
                logging.error(' - Error: ' + str(e))
    
    # End grid search
    elapsed = timeit.default_timer() - start_time
    logging.info(' - Grid search elapsed time: ' + str(elapsed) + ' s')
    
    return scores

# Core function - Make predictions
def make_predictions(curr_disease, entity, model, n_forecast, ci_alpha):
    
    # Get forecast n steps ahead in future (1 year)
    pred = model.get_forecast(steps=n_forecast)
    y_forecasted = np.array([max(round(p), 0) for p in pred.predicted_mean])
    
    # Get confidence intervals of forecasts
    pred_df = pd.DataFrame(y_forecasted, columns=['forecast'])
    pred_df = pred_df.set_index(pred.predicted_mean.index)
    pred_ci = pred.conf_int(alpha=1-ci_alpha)
    pred_df['ci_inf'] = pred_ci.iloc[:, 0]
    pred_df['ci_sup'] = pred_ci.iloc[:, 1]
    
    # Save results
    filename = '../result/' + curr_disease.lower() + '/' + entity.lower() + '_forecast.csv'
    save_df_to_csv_file(filename, pred_df)

# Core function - Check if the entity has permission to be processed
def check_permission(entity):
    valid_entity = []
    if len(valid_entity) == 0 or entity in valid_entity:
        return True
    return False

# Core function - Create models by entities
def create_models(curr_disease, data_list, perc_test, n_forecast, ci_alpha):
    best_models = dict()
    
    try:
        for entity, data in data_list.items():            
            
            # Check permission to be processed
            if not check_permission(entity):
                continue
            
            logging.info(' = Entity: ' + entity)
            
            # Cooking time-series data with frequency
            filter_date = pd.to_datetime('2020-01-01').date()
            series_data = data['value']
            series_data = series_data.loc[series_data.index < filter_date]
            series_data = series_data.asfreq(freq='4W')
            
            # Training and testing process
            scores = arima_grid_search(series_data, perc_test)
            
            # Create best model
            if len(scores):
                scores = sorted(scores, key = lambda i: i['mape'])
                
                # Save best 10 model params
                n = min(len(scores), 10)
                logging.info(' = Save best ' + str(n) + ' models')
                for score in scores[:n]:
                    logging.info(' - ' + str(score))
                
                # Create best model
                best_params = scores[0]
                model = sm.tsa.statespace.SARIMAX(series_data, order=best_params['order'], seasonal_order=best_params['seasonal_order'], 
                                                  enforce_stationarity=False, enforce_invertibility=False)
                model = model.fit()
                best_models[entity] = best_params
                
                # Make predictions
                logging.info(' = Make predictions')
                make_predictions(curr_disease, entity, model, n_forecast, ci_alpha)
                
    except Exception as e:
        logging.error(' - Error: ' + str(e))
        best_models[entity] = { 'result': str(e) }
    
    return best_models

# Core function - Save to CSV file the hyperparameters of selected models 
def save_results(curr_disease, data):
    df = pd.DataFrame.from_dict(data, orient='index')
    
    # Populate final dataframe
    for ix, row in df.iterrows():
        order = row['order']
        seasonal_order = row['seasonal_order']
        df.at[ix, 'p'] = order[0]
        df.at[ix, 'd'] = order[1]
        df.at[ix, 'q'] = order[2]
        df.at[ix, 'Sp'] = seasonal_order[0]
        df.at[ix, 'Sd'] = seasonal_order[1]
        df.at[ix, 'Sq'] = seasonal_order[2]
        df.at[ix, 'freq'] = seasonal_order[3]
    
    # Remove unused columns
    df.drop("order", axis=1, inplace=True)
    df.drop("seasonal_order", axis=1, inplace=True)
    
    # Persist data
    filename = '../result/' + curr_disease.lower() + '/model_params.csv'
    save_df_to_csv_file(filename, df)

#####################
### START PROGRAM ###
#####################
logging.basicConfig(filename="log/log_file.log", level=logging.INFO)
logging.info('>> START PROGRAM: ' + str(datetime.now()))

# 1. Set current disease
curr_disease = 'TUBERCULOSIS'
logging.info(' = Disease: ' + curr_disease)
create_folder('../result/' + curr_disease.lower())

# 2. Get list of datasets by entities
logging.info(' = Read data by entity - ' + str(datetime.now()))
filename = '../data/' + curr_disease.lower() + '_dataset.csv'
data_list = get_data_by_entity(filename)

# 3. Create best model
logging.info(' = Create best models - ' + str(datetime.now()))
perc_test = 0.20
n_forecast = 13
ci_alpha = 0.9
best_models = create_models(curr_disease, data_list, perc_test, n_forecast, ci_alpha)

# 4. Save hyperparameters of selected models
logging.info(' = Save hyperparameters of selected models - ' + str(datetime.now()))
save_results(curr_disease, best_models)

logging.info(">> END PROGRAM: " + str(datetime.now()))
logging.shutdown()
#####################
#### END PROGRAM ####
#####################
