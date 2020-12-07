# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 2.1.0
    Created on: Sep 09, 2020
    Updated on: Nov 23, 2020
    Description: Main class of the predictive-engine solution.
"""

# Import Python
import os
import logging
import pandas as pd
import concurrent.futures
from multiprocessing import cpu_count
from datetime import datetime

# Import custom libraries
import util_lib as ul
import pred_engine as pe

######################
### CORE FUNCTIONS ###
######################

# Core function - Create results folders
def create_result_folders(folder_name):
    folder_path = '../result/' + folder_name
    ul.create_folder(folder_path)

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

# Core function - Read the CSV dataset and convert it to a dictionary by entity
def get_data_by_entity(filename, entity_filter):
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
                if (len(entity_filter) == 0 or entity in entity_filter) and (entity in divipola_code.keys()):
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
                    print(' = Entity without permission to be processed: ' + entity)
    
    # Return dict of entity, data pairs
    return data_list, full_data

# Core function - Mask to the predictive engine
def create_models(args):
    entity, data, curr_analysis, perc_test, mape_threshold, ts_tolerance, n_forecast, ci_alpha, partial_end_date, full_init_date = args
    print(' = Entity: ' + entity + ' - ' + str(datetime.now()))
    return pe.create_models(entity, data, curr_analysis, perc_test, mape_threshold, ts_tolerance, n_forecast, ci_alpha, partial_end_date, full_init_date)

# Core function - Create SARIMA model in Parallel
def parallel_create_models(data_list, curr_analysis, n_process, kwargs):
    best_models = dict()
    model_data = pd.DataFrame(columns=['date', 'entity', 'forecast', 'ci_inf', 'ci_sup'])
    
    # Read local event variables
    perc_test = kwargs['perc_test']
    mape_threshold = kwargs['mape_threshold']
    ts_tolerance = kwargs['ts_tolerance']
    n_forecast = kwargs['n_forecast']
    ci_alpha = kwargs['ci_alpha']
    partial_end_date = kwargs['partial_end_date']
    full_init_date = kwargs['full_init_date']
    
    # Create list of params for threads
    params = []
    for entity, data in data_list.items():
        params.append([entity, data, curr_analysis, perc_test, mape_threshold, ts_tolerance, n_forecast, ci_alpha, partial_end_date, full_init_date])
    
    # Start compute cycle
    try:
        result_data = []
        if n_process > 1:
            logging.info(' - Start parallel cycle')
            if __name__ == '__main__':
                with concurrent.futures.ThreadPoolExecutor(max_workers=n_process) as executor:
                    result_data = executor.map(create_models, params)
            logging.info(' - End parallel cycle')
        else:
            logging.info(' - Start sequential cycle')
            result_data = [create_models(param) for param in params]
            logging.info(' - End sequential cycle')
        
        # Save results in save-mode
        for entity, best_params, pred_df in result_data:
            best_models[entity] = best_params
            model_data = model_data.append(pred_df)
        
    except Exception as e:
        logging.error(' - Create models error: ' + str(e))
        
    # Return results
    return best_models, model_data

# Core function - Save to CSV file the hyperparameters of selected models 
def save_results(curr_event, curr_analysis, best_models, full_data, exec_date):
    exec_col = 'exec_date'
    
    # Save best models
    best_models = {k: v for k, v in best_models.items() if v is not None}
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
        df.insert(0, exec_col, str(exec_date))
        
        # Persist data
        filename = '../result/' + curr_event + '/model_params_' + curr_analysis + '.csv'
        ul.save_df_to_csv_file(filename, df)
    
    # Save model data results
    if full_data is not None and len(full_data):
        
        # Post processing of the data
        full_data.reset_index(inplace=True)
        full_data.insert(0, exec_col, str(exec_date))
        
        # Persist data
        filename = '../result/' + curr_event + '/result_data_' + curr_analysis + '.csv'
        ul.save_df_to_csv_file(filename, full_data, False)

#####################
### START PROGRAM ###
#####################
if __name__ == "__main__":
    
    # 0. Program variables
    log_path = 'log/log_file.log'
    config_path = 'config/config.json'
    logging.basicConfig(filename=log_path, level=logging.INFO)
    logging.info('>> START PROGRAM: ' + str(datetime.now()))
    
    # 1. Read config params
    setup_params = ul.get_dict_from_json(config_path)
    event_list = setup_params['event_list']
    entity_filter = setup_params['entity_filter']
    n_process = max(min(int(setup_params['n_process']), cpu_count() - 1), 1)
    
    # 2. Loop through entities 
    for curr_event in event_list:
        event_name = curr_event['name'].lower()
        
        if event_name and curr_event['enabled']:
            
            # Save event params
            logging.info(' = Event: ' + event_name)
            logging.info(curr_event)
            
            # 3. Create result folders
            create_result_folders(event_name)
            
            # 4. Get list of datasets by entities
            logging.info(' = Read data by entity - ' + str(datetime.now()))
            filename = '../data/' + event_name + '_dataset.csv'
            data_list, base_data = get_data_by_entity(filename, entity_filter)
    
            # Get initial execute date
            exec_date = datetime.now()
            analysis_list = curr_event['analysis_list']
            
            # 5. Loop through entities
            for curr_analysis in analysis_list:
                curr_analysis = curr_analysis.lower()
                logging.info(' = Analysis: ' + curr_analysis)
                
                # 6. Create best model
                logging.info(' = Create best models >> ' + curr_analysis + ' - '+ str(datetime.now()))
                best_models, model_data = parallel_create_models(data_list, curr_analysis, n_process, curr_event)
                
                # 7. Save hyperparameters of selected models
                logging.info(' = Save selected models results - ' + str(datetime.now()))
                full_data = ul.merge_data(df1=base_data, df2=model_data, index=['date', 'entity', 'year', 'period'])
                save_results(event_name, curr_analysis, best_models, full_data, exec_date)
        else:
            logging.info(' = Event: ' + event_name + ' will not be processed.')
            print(' = Event', event_name, 'will not be processed.')
            
    logging.info(">> END PROGRAM: " + str(datetime.now()))
    logging.shutdown()
#####################
#### END PROGRAM ####
#####################
