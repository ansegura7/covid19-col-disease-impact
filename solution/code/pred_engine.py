# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.0.0
    Created on: Sep 09, 2020
    Updated on: Oct 06, 2020
    Description: Predictive engine for both scenarios (partial or w/o COVID and full or w COVID)..
"""

# Import Python
import logging
import pandas as pd
import numpy as np
import scipy.stats as ss
import itertools
import timeit
from math import ceil
from warnings import filterwarnings

# Import custom libraries
import util_lib as ul

# Import Time Series libraries
import statsmodels.api as sm

# Global variables
log_path = 'log/log_file.log'
logging.basicConfig(filename=log_path, level=logging.INFO)

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
def arima_grid_search(series_data, perc_test, mape_threshold, ts_tolerance):
    scores = []
    
    # Specify to ignore warning messages
    filterwarnings("ignore")
    
    # Start prediction from...
    ix_test = ceil(len(series_data) * (1 - perc_test))
    start_date = series_data.index[ix_test]
    
    # Calculation params
    method = 'SARIMA'
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
                    
                    # Compute tracking signal (TS) for prediction
                    ts_period = ul.tracking_signal(y_truth, y_forecasted, ts_tolerance)
                    
                    # Save result if model MAPE is greater than threshold
                    if mape > mape_threshold and ts_period > 0:
                        scores.append( {'method': method, 'order': param, 'seasonal_order': param_seasonal,
                                        'var_coef_diff': round(vc_diff, 4), 'tracking_signal': ts_period,
                                        'rmse': round(rmse, 4), 'mape': round(mape, 4), 'aic': round(model.aic, 4), 'bic': round(model.bic, 4)} )
                    
            except Exception as e:
                print(' - Grid Search Error: ' + str(e))
    
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
def create_models(entity, data, curr_algo, perc_test, mape_threshold, ts_tolerance, n_forecast, ci_alpha):
    best_params = None
    pred_df = None
    
    try:
        logging.info(' = Entity: ' + entity)
        
        # Cooking time-series data with frequency
        series_data = data['value']
        series_data = series_data.asfreq(freq='4W')
        
        # Filter data (Partial mode)   
        if curr_algo == 'partial':
            filter_date = pd.to_datetime('2019-12-27')
            series_data = series_data.loc[series_data.index < filter_date]            
        
        # Begin grid search: Training and testing process
        start_time = timeit.default_timer()
        scores = arima_grid_search(series_data, perc_test, mape_threshold, ts_tolerance)
        elapsed = timeit.default_timer() - start_time
        logging.info(' - Grid search elapsed time: ' + str(elapsed) + ' s, for: ' + entity)
    
        # Create best model
        if len(scores):
            scores = sorted(scores, key = lambda i: i['mape'])
            
            # Save best 10 model params
            n = min(len(scores), 10)
            logging.info(' = Save best ' + str(n) + ' models for: ' + entity)
            logging.info(scores[:n])
            
            # Create best model
            best_params = scores[0]
            model = sm.tsa.statespace.SARIMAX(series_data, order=best_params['order'], seasonal_order=best_params['seasonal_order'], 
                                              enforce_stationarity=False, enforce_invertibility=False).fit()
            
            # Make predictions
            logging.info(' = Make predictions for: ' + entity)
            year = 2020
            pred_df = make_predictions(entity, model, n_forecast, ci_alpha, year)
        
    except Exception as e:
        logging.error(' - Error in: ' + entity + ': ' + str(e))
    
    # Return 3-tupla
    return (entity, best_params, pred_df)
