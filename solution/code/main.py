# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.1.0
    Created on: Sep 09, 2020
    Updated on: Oct 06, 2020
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
from math import ceil
from warnings import filterwarnings

# Import custom libraries
import util_lib as ul

# Import Time Series libraries
import statsmodels.api as sm

######################
### CORE FUNCTIONS ###
######################

# Core function - Group data by period
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

# Core function - Create results folders
def create_result_folders(folder_name):
    folder_path = '../result/' + folder_name.lower()
    ul.create_folder(folder_path)

# Core function - Read the CSV dataset and convert it to a dictionary by entity
def get_data_by_entity(filename):
    data_list = dict()
    full_data = pd.DataFrame(columns=['date', 'entity', 'year', 'period', 'value'])
    
    # Validation
    if os.path.exists(filename):
        
        # Read divipola dictionary
        divipola_code = dict()
        divipola_data = pd.read_csv('config/divipola.csv')
        
        for ix, row in divipola_data.iterrows():
            entity = row['entity']
            code = row['divipola']
            divipola_code[entity] = code
        
        # Read data from CSV dataset
        raw_data = pd.read_csv(filename, parse_dates=['date'])
        
        # Filter data by entity
        if len(raw_data):
            entity_list = raw_data['entity'].unique()
            
            # Filtering and grouping data by entity
            for entity in entity_list:
                
                # Check permission to be processed
                if check_permission(entity) and entity in divipola_code.keys():
                    entity_code = str(divipola_code[entity]).zfill(5)
                    
                    entity_data = raw_data[raw_data['entity'] == entity]
                    entity_data = group_data_by_period(entity_data)        
                    data_list[entity_code] = entity_data
                    
                    # Keep entity data
                    temp_data = entity_data.copy()
                    temp_data.reset_index(inplace=True)
                    temp_data['entity'] = entity_code
                    temp_data = temp_data.reindex(columns=full_data.columns)
                    full_data = full_data.append(temp_data)
                    print((entity, entity_code), '->', len(temp_data), '=', len(full_data))
                else:
                    logging.info(' = Entity without permission to be processed: ' + entity)
    
    # Return dict of entity, data pairs
    return data_list, full_data

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
                    rmse = ul.calc_rmse(y_truth, y_forecasted)
                    mape = ul.calc_mape(y_truth, y_forecasted)
                    
                    # Validate prediction with Dynamic Forecast
                    pred_dynamic = model.get_prediction(start=start_date, dynamic=True, full_results=True)
                    y_forecasted = np.array([max(round(p), 0) for p in pred_dynamic.predicted_mean])
                    
                    # Compute the errors 2
                    rmse = (rmse + ul.calc_rmse(y_truth, y_forecasted)) / 2
                    mape = (mape + ul.calc_mape(y_truth, y_forecasted)) / 2
                    
                    # Compute variation coefficient difference
                    ts_var_coef = ss.variation(series_data.values)
                    pred_var_coef = ss.variation(y_forecasted)
                    vc_diff = ts_var_coef
                    if not np.isnan(pred_var_coef):
                        vc_diff = abs(ts_var_coef - pred_var_coef)
                    
                    # Compute tracking signal for prediction
                    ts_period = ul.tracking_signal(y_truth, y_forecasted, ci_tolerance)
                    
                    # Save result if model MAPE is greater than threshold
                    if mape > threshold and ts_period > 0:
                        scores.append( {'method': method, 'order': param, 'seasonal_order': param_seasonal,
                                        'var_coef_diff': round(vc_diff, 4), 'tracking_signal': ts_period,
                                        'rmse': round(rmse, 4), 'mape': round(mape, 4), 'aic': round(model.aic, 4), 'bic': round(model.bic, 4)} )
                    
            except Exception as e:
                logging.error(' - Error: ' + str(e))
    
    # End grid search
    elapsed = timeit.default_timer() - start_time
    logging.info(' - Grid search elapsed time: ' + str(elapsed) + ' s')
    
    return scores

# Core function - Make predictions
def make_predictions(entity, model, n_forecast, ci_alpha, year):
    
    # Get forecast n steps ahead in future (1 year)
    pred = model.get_forecast(steps=n_forecast)
    y_forecasted = np.array([max(round(p), 0) for p in pred.predicted_mean])
    pred_ci = pred.conf_int(alpha=(1 - ci_alpha))
    
    # Create forecast data with confidence intervals
    fr_data = {'date': pred.predicted_mean.index, 'entity': entity, 'year': year, 'period': np.arange(1, n_forecast + 1), 
               'forecast': y_forecasted, 'ci_inf': pred_ci.iloc[:, 0].values, 'ci_sup': pred_ci.iloc[:, 1].values}
    
    # Create Dataframe
    pred_df = pd.DataFrame(fr_data)
    
    # Replace negative values by zero
    num_data = pred_df._get_numeric_data()
    num_data[num_data < 0] = 0
    
    # Return prediction dataframe
    return pred_df

# Core function - Create models by entities
def create_models(curr_event, data_list, curr_algo, perc_test, n_forecast, ci_alpha):
    best_models = dict()
    model_data = pd.DataFrame(columns=['date', 'entity', 'forecast', 'ci_inf', 'ci_sup'])
    
    try:
        for entity, data in data_list.items():
            logging.info(' = Entity: ' + entity)
            
            # Cooking time-series data with frequency
            series_data = data['value']
            series_data = series_data.asfreq(freq='4W')

            # Filter data (Partial mode)            
            if curr_algo == 'PARTIAL':
                filter_date = pd.to_datetime('2019-12-27').date()
                series_data = series_data.loc[series_data.index < filter_date]            
            
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
                year = 2020
                pred_df = make_predictions(entity, model, n_forecast, ci_alpha, year)
                model_data = model_data.append(pred_df)
                
    except Exception as e:
        logging.error(' - Error: ' + str(e))
        best_models[entity] = { 'result': str(e) }
    
    return best_models, model_data

# Core function - Save to CSV file the hyperparameters of selected models 
def save_results(curr_event, curr_algo, best_models, full_data):
    
    # Save best models
    if len(best_models):
        df = pd.DataFrame.from_dict(best_models, orient='index')
        
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
        filename = '../result/' + curr_event.lower() + '/model_params_' + curr_algo.lower() + '.csv'
        ul.save_df_to_csv_file(filename, df)

    # Save model data results
    if len(full_data):
        filename = '../result/' + curr_event.lower() + '/result_data_' + curr_algo.lower() + '.csv'
        ul.save_df_to_csv_file(filename, full_data, True)

# Core function - Check if the entity has permission to be processed
def check_permission(entity):
    if len(entity_filter) == 0 or entity in entity_filter:
        return True
    return False

#####################
### START PROGRAM ###
#####################
logging.basicConfig(filename="log/log_file.log", level=logging.INFO)
logging.info('>> START PROGRAM: ' + str(datetime.now()))

# 1. Read config params
yaml_path = 'config\config.yml'
setup_params = ul.get_dict_from_yaml(yaml_path)
entity_filter = setup_params['entity_filter']
event_list = setup_params['event_list']
algo_type = setup_params['algo_type']
perc_test = setup_params['perc_test']
n_forecast = setup_params['n_forecast']
ci_alpha = setup_params['ci_alpha']
threshold = setup_params['mape_threshold']
ci_tolerance = setup_params['ci_tolerance']

# 2. Set current event (disease)
curr_event = event_list[0]
logging.info(' = Event: ' + curr_event)
create_result_folders(curr_event)

# 3. Get list of datasets by entities
logging.info(' = Read data by entity - ' + str(datetime.now()))
filename = '../data/' + curr_event.lower() + '_dataset.csv'
data_list, base_data = get_data_by_entity(filename)

# 4. Create best model
curr_algo = algo_type[1]
logging.info(' = Create best models >> ' + curr_algo + ' - '+ str(datetime.now()))
best_models, model_data = create_models(curr_event, data_list, curr_algo, perc_test, n_forecast, ci_alpha)

# 5. Save hyperparameters of selected models
logging.info(' = Save selected models results - ' + str(datetime.now()))
full_data = ul.merge_data(df1=base_data, df2=model_data, index=['date', 'entity', 'year', 'period'])
save_results(curr_event, curr_algo, best_models, full_data)

logging.info(">> END PROGRAM: " + str(datetime.now()))
logging.shutdown()
#####################
#### END PROGRAM ####
#####################
