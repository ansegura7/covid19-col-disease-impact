# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.0.0
    Created on: Nov 23, 2020
    Updated on: Dec 11, 2020
    Description: Main class of the descriptive-engine solution.
"""

# Import Python
import os
import logging
import pandas as pd
import numpy as np
import scipy.stats as ss
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

# Core function - Get population by entity and year
def get_population_by_entity():
    pop_data = {}
    
    raw_data = pd.read_csv('config/population.csv')
    
    if len(raw_data):
        for ix, row in raw_data.iterrows():
            code = str(row['divipola'])
            year = str(row['year'])
            pop_value = row['population']
            
            # Apply data quality to code
            if len(code) == 1:
                code = '0' + code + '000'
            elif len(code) == 2:
                code = code + '000'
            elif len(code) == 4:
                code = '0' + code
            
            # Save key, population pair
            key = code + '_' + year
            pop_data[key] = pop_value
            
    return pop_data

# Core function - Calculate descriptive stats by entity and period
def calc_desc_stats(data_list, pop_data, n_years=10, div = 100000):
    stats_data = pd.DataFrame(columns=['entity', 'period', 'total', 'mean', 'stdev', 'min', 'p25', 'p50', 'p75', 'max', 'no_data'])
    
    # Grouping data by periods
    for entity, data in data_list.items():        
        n_rows = len(data)
        stats = dict()
        values = []
        all_values = []
        period = 1
        no_data = 0
        
        for week in range(1, 54):
            for ix in range(n_rows):
                year = data.iloc[ix]['year'] 
                
                if (len(values) == 4 * n_years and week != 53):
                    stats[str(period)] = { 'values': values, 'no_data': no_data }
                    period += 1
                    values = []
                    no_data = 0
                    
                key = entity + '_' + str(year)
                entity_pop = pop_data[key]
                value = round(data.iloc[ix][str(week)] / entity_pop * div, 4)
                
                if week != 53 or value > 0:
                    values.append(value)
                    all_values.append(value)
                    
                    if value == 0:
                        no_data += 1
        
        stats[str(period)] = { 'values': values, 'no_data': no_data }
        var_coef = round(100.0 * ss.variation(all_values), 4)
        
        # Loop through periods
        for key, item in stats.items():
            values = item['values']
            no_data = item['no_data']
            values.sort()
            
            # Calc stats
            total = round(sum(values), 4)
            mean = round(np.mean(values), 4)
            stdev = round(np.std(values), 4)
            min_value = min(values)
            max_value = max(values)
            p25 = np.percentile(values, 25)
            p50 = np.percentile(values, 50)
            p75 = np.percentile(values, 75)
            
            # Save row item
            row_item = {'entity': entity, 'period': key, 'total': total, 'mean': mean, 'stdev': stdev, 'min': min_value, 
                        'p25': p25, 'p50':p50, 'p75': p75, 'max': max_value, 'no_data': no_data, 'var_coef': var_coef}
            stats_data = stats_data.append(row_item, ignore_index=True)
     
    return stats_data

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
    event_list = ['TUBERCULOSIS']
    entity_filter = []
    
    # 2. Loop through entities
    for curr_event in event_list:
        event_name = curr_event.lower()
        exec_date = datetime.now()
        logging.info(' = Event: ' + event_name + ' - ' + str(exec_date))
        
        # 3. Create result folders
        create_result_folders(event_name)
        
        # 4. Get list of datasets by entities
        logging.info(' = Read data by entity - ' + str(datetime.now()))
        filename = '../data/' + event_name + '_dataset.csv'
        data_list = get_data_by_entity(filename, entity_filter)
        
        # 5. Get population by entity and year
        pop_data = get_population_by_entity()
        
        # 6. Calculate descriptive stats
        logging.info(' = Calculate descriptive stats - ' + str(datetime.now()))
        full_data  = calc_desc_stats(data_list, pop_data)
        
        # 7. Save result stats
        logging.info(' = Save result stats - ' + str(datetime.now()))
        save_results(event_name, full_data, exec_date)
    
    logging.info(">> END PROGRAM: " + str(datetime.now()))
    logging.shutdown()
#####################
#### END PROGRAM ####
#####################
