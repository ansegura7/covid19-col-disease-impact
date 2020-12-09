# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.0.0
    Created on: Nov 23, 2020
    Updated on: Nov 23, 2020
    Description: Main class of the descriptive-engine solution.
"""

# Import Python
import os
import logging
import pandas as pd
from datetime import datetime

# Import custom libraries
import util_lib as ul

######################
### CORE FUNCTIONS ###
######################

# Core function - Create results folders
def create_result_folders(folder_name):
    folder_path = '../result/' + folder_name
    ul.create_folder(folder_path)

# Core function - Read the CSV dataset and convert it to a dictionary by entity
def get_data_by_entity(filename, entity_filter):
    data_list = dict()
    
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
        raw_data = pd.read_csv(filename)
        
        # Filter data by entity
        if len(raw_data):
            entity_list = raw_data['entity'].unique()
            
            # Filtering and grouping data by entity
            for entity in entity_list:
                
                # Check permission to be processed
                if (len(entity_filter) == 0 or entity in entity_filter) and (entity in divipola_code.keys()):
                    entity_code = str(divipola_code[entity]).zfill(5)
                    
                    entity_data = raw_data[raw_data['entity'] == entity]
                    entity_data = entity_data.groupby(['entity', 'year']).agg('sum')
                    entity_data.reset_index(inplace=True)
                    data_list[entity_code] = entity_data
                    print((entity, entity_code), '->', len(entity_data))
                else:
                    print(' = Entity without permission to be processed: ' + entity)
    
    return data_list

# Core function - Calculate descriptive stats by entity
def calc_desc_stats(data_list, n_years=10):
    data = pd.DataFrame(columns=['entity', 'period', 'mean', 'dev', 'min', 'q25', 'q50', 'q75', 'max', 'no_data'])
    
    for entity, data in data_list.items():
        print(entity, len(data))
    
    return data

# Core function - Save to CSV file the result stats by entity
def save_results(curr_event, full_data, exec_date):
    exec_col = 'exec_date'
    
    # Save model data results
    if full_data is not None and len(full_data):
        
        # Post processing of the data
        full_data.reset_index(inplace=True)
        full_data.insert(0, exec_col, str(exec_date))
        
        # Persist data
        filename = '../result/' + curr_event + '/result_data.csv'
        ul.save_df_to_csv_file(filename, full_data, False)

#####################
### START PROGRAM ###
#####################
if __name__ == "__main__":
    
    # 0. Program variables
    log_path = 'log/log_file.log'
    yaml_path = 'config/config.yml'
    logging.basicConfig(filename=log_path, level=logging.INFO)
    logging.info('>> START PROGRAM: ' + str(datetime.now()))
    
    # 1. Read config params
    exec_date = datetime.now()
    event_name = 'TUBERCULOSIS'
    entity_filter = []
    
    # 2. Set current event (from setup file)
    event_name = event_name.lower()
    logging.info(' = Event: ' + event_name)
    
    # 3. Create result folders
    create_result_folders(event_name)
    
    # 4. Get list of datasets by entities
    logging.info(' = Read data by entity - ' + str(datetime.now()))
    filename = '../data/' + event_name + '_dataset.csv'
    data_list = get_data_by_entity(filename, entity_filter)
    
    # 5. Calculate descriptive stats
    logging.info(' = Calculate descriptive stats - ' + str(datetime.now()))
    full_data  = calc_desc_stats(data_list)
    
    # 7. Save hyperparameters of selected models
    logging.info(' = Save selected models results - ' + str(datetime.now()))
    save_results(event_name, full_data, exec_date)
    
    logging.info(">> END PROGRAM: " + str(datetime.now()))
    logging.shutdown()
#####################
#### END PROGRAM ####
#####################
