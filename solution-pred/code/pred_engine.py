# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.3.0
    Created on: Sep 09, 2020
    Updated on: Nov 06, 2020
    Description: Predictive engine for both scenarios (partial or w/o COVID and full or w COVID)..
"""

# Import Python
import logging
import pandas as pd
import numpy as np
import scipy.stats as ss
import timeit
import statsmodels.api as sm
from math import ceil
from warnings import filterwarnings

# Import Parallel libraries
from multiprocessing import cpu_count
from joblib import Parallel
from joblib import delayed

# Import custom libraries
import util_lib as ul

# Global variables
log_path = 'log/log_file.log'
logging.basicConfig(filename=log_path, level=logging.INFO)

# Core function - Create a set of SARIMA configs to try
def sarima_configs(seasonal=[13]):
    models = []
    
    # Define config lists
    p_params = [0, 1, 2]
    d_params = [0, 1, 2]
    q_params = [0, 1, 2]
    P_params = [0, 1, 2]
    D_params = [0, 1, 2]
    Q_params = [0, 1, 2]
    m_params = seasonal
    #t_params = ['n','c','t','ct']
    
    # Create config instances
    for p in p_params:
        for d in d_params:
            for q in q_params:
                for P in P_params:
                    for D in D_params:
                        for Q in Q_params:
                            for m in m_params:
                                #for t in t_params:
                                cfg = [(p,d,q), (P,D,Q,m), 'n']
                                models.append(cfg)
    
    return models

# Core function - Score a model
def sarima_score_model(series_data, start_date, config, mape_threshold, ts_tolerance):
    result = {}
    method = 'SARIMA'
    
    try:
        # Create and fit model
        order, sorder, trend = config
        model = sm.tsa.statespace.SARIMAX(series_data, order=order, seasonal_order=sorder, #trend=trend, 
                                          enforce_stationarity=False, enforce_invertibility=False)
        model = model.fit(disp=False, iprint=False)
        
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
            # rmse = (0.4 * rmse + 0.6 * ul.calc_rmse(y_truth, y_forecasted)) / 2
            # mape = (0.4 * mape + 0.6 * ul.calc_mape(y_truth, y_forecasted)) / 2
            rmse = (rmse + ul.calc_rmse(y_truth, y_forecasted)) / 2
            mape = (mape + ul.calc_mape(y_truth, y_forecasted)) / 2
            
            # Compute variation coefficient difference
            ts_var_coef = ss.variation(series_data.values)
            pred_var_coef = ss.variation(y_forecasted)
            vc_diff = ts_var_coef
            if not np.isnan(pred_var_coef):
                vc_diff = abs(ts_var_coef - pred_var_coef)
            
            # Compute tracking signal (TS) for prediction
            ts_period, ts_total = ul.tracking_signal(y_truth, y_forecasted, ts_tolerance)
            
            # Save result if model MAPE is greater than threshold
            if mape > mape_threshold and ts_period > 0:
                result = {'method': method, 'order': order, 'seasonal_order': sorder, 'trend': trend, 
                          'var_coef_diff': round(vc_diff, 4), 'tracking_signal': ts_period, 'tracking_signal_total': ts_total, 
                          'rmse': round(rmse, 4), 'mape': round(mape, 4), 'aic': round(model.aic, 4), 'bic': round(model.bic, 4)}
        
    except Exception as e:
        result = {}
        print(' - Grid Search Error: ' + str(e))
        
    return result
    
# Core function - Parameter selection for the ARIMA Time Series model
def sarima_grid_search(series_data, perc_test, mape_threshold, ts_tolerance, parallel=False):
    scores = []
    
    # Specify to ignore warning messages
    filterwarnings("ignore")
    
    # Start prediction from...
    ix_test = ceil(len(series_data) * (1 - perc_test))
    start_date = series_data.index[ix_test]
    
    # Calculation params
    data_freq = 13
    pdq_params = sarima_configs(seasonal=[data_freq])
    print(' = n params:', len(pdq_params))
    
    # Grid search
    if parallel:
        # Execute configs in parallel
        n_cpu = cpu_count() - 1
        executor = Parallel(n_jobs=n_cpu, backend='multiprocessing')
        tasks = (delayed(sarima_score_model)(series_data, start_date, params, mape_threshold, ts_tolerance) for params in pdq_params)
        scores = executor(tasks)
    else:
        # Execute configs in sequence
        scores = [sarima_score_model(series_data, start_date, params, mape_threshold, ts_tolerance) for params in pdq_params]
    
    # Remove empty results
    scores = [score for score in scores if len(score)]
    
    return scores

# Core function - Make predictions
def make_predictions(entity, model, n_forecast, ci_alpha, last_year, last_period):
    
    # Get forecast n steps ahead in future (1 year)
    pred = model.get_forecast(steps=n_forecast)
    y_forecasted = np.array([max(round(p), 0) for p in pred.predicted_mean])
    pred_ci = pred.conf_int(alpha=(1 - ci_alpha))
    
    # Create year-period pairs for prediction
    period_list = []
    year_list = []
    
    for i in range(1, n_forecast + 1):
        last_period += 1
        if last_period == 14:
            last_period = 1
            last_year += 1
        
        period_list.append(last_period)
        year_list.append(last_year)
    
    # Create forecast data with confidence intervals
    fr_data = {'date': pred.predicted_mean.index, 'entity': entity, 'year': year_list, 'period': period_list , 
               'forecast': y_forecasted, 'ci_inf': pred_ci.iloc[:, 0].values, 'ci_sup': pred_ci.iloc[:, 1].values}
    
    # Create Dataframe from (dict) data
    pred_df = pd.DataFrame(fr_data)
    
    # Replace negative values by zero
    num_data = pred_df._get_numeric_data()
    num_data[num_data < 0] = 0
    
    # Return prediction dataframe
    return pred_df

# Core function - Create models by entities
def create_models(entity, data, curr_analysis, perc_test, mape_threshold, ts_tolerance, n_forecast, ci_alpha, partial_end_date, full_init_date):
    best_params = None
    pred_df = None
    
    try:
        logging.info(' = Entity: ' + entity)
        
        # Cooking time-series data with frequency
        last_year, last_period, last_value = data.iloc[len(data)-1]
        series_data = data['value']
        series_data = series_data.asfreq(freq='4W')
        
        # Filter data (Partial mode)   
        if curr_analysis == 'partial':
            filter_date = pd.to_datetime(partial_end_date)
            last_year, last_period = filter_date.year, 13
            series_data = series_data.loc[series_data.index < filter_date]
        
        # Begin grid search: Training and testing process
        start_time = timeit.default_timer()
        scores = sarima_grid_search(series_data, perc_test, mape_threshold, ts_tolerance, parallel=True)
        elapsed = timeit.default_timer() - start_time
        print(' = n scores:', len(scores))
        logging.info(' - Grid search elapsed time: ' + str(elapsed) + ' s, for: ' + entity + ', n models: ' +  str(len(scores)))
    
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
                                              trend=best_params['trend'], enforce_stationarity=False, enforce_invertibility=False)
            model = model.fit(disp=False, iprint=False)
            
            # Make predictions
            logging.info(' = Make predictions for: ' + entity)
            pred_df = make_predictions(entity, model, n_forecast, ci_alpha, last_year, last_period)
        
    except Exception as e:
        logging.error(' - Error in: ' + entity + ': ' + str(e))
    
    # Return 3-tupla
    return (entity, best_params, pred_df)
