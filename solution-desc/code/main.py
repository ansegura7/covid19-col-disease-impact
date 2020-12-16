# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.1.0
    Created on: Nov 23, 2020
    Updated on: Dec 14, 2020
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
def get_data_by_entity(filename, entity_filter, frequency):
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
                    
                    # Filter data by entity
                    entity_data = raw_data[raw_data['entity'] == entity]
                    entity_data = entity_data.groupby(['entity', 'year']).agg('sum')
                    entity_data.reset_index(inplace=True)
                    
                    # Grouping data by frequency
                    if frequency == 'weekly':
                        temp_data = pd.DataFrame(columns=['entity', 'year', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13'])                   
                        
                        # Grouping data by periods
                        for ix, row_data in entity_data.iterrows():
                            year = row_data['year']
                            values = []
                            periods = []
                            
                            for week in range(1, 54):
                                value = row_data[str(week)]
                                values.append(value)
                                
                                if (len(values) == 4 and week != 52) or (len(values) == 5 and week == 53):
                                    total = sum(values)
                                    periods.append(total)
                                    values = []
                            
                            # Save data row
                            temp_data.loc[len(temp_data)] = [entity, year] + periods
                    
                    elif frequency == 'periodically':
                        temp_data = entity_data.copy()
                    
                    # Save data
                    data_list[entity_code] = temp_data
                    print((entity, entity_code), '->', len(temp_data))
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
            
            # Apply data quality to code
            if len(code) == 1:
                code = '0' + code + '000'
            elif len(code) == 2:
                code = code + '000'
            elif len(code) == 4:
                code = '0' + code
                
            # Get population data
            for year in range(2010, 2021):
                year = str(year)
                pop_value = row[year]
            
                # Save key, population pair
                key = code + '_' + year
                pop_data[key] = pop_value
    
    return pop_data

# Core function - Calculate descriptive stats by entity and period
def calc_desc_stats(data_list, pop_data, rate_enable, max_year):
    gr_data = pd.DataFrame(columns=['entity', 'year', 'period', 'total'])
    stats_data = pd.DataFrame(columns=['entity', 'period', 'total', 'mean', 'stdev', 'min', 'p25', 'p50', 'p75', 'max', 'no_data', 'pv_period', 'pv_value', 'pv_min_lim', 'pv_max_lim'])
    
    # Loop through year, weeks
    for entity, data in data_list.items():
        n_rows = len(data)
        temp_df = pd.DataFrame(columns=['year', 'period', 'value'])
        
        # Grouping data by periods
        for ix in range(n_rows):
            row_data = data.iloc[ix]
            year = row_data['year']
            key = entity + '_' + str(year)
            entity_pop = pop_data[key]
            
            for period in range(1, 14):
                total = row_data[str(period)]

                # Change totals per rates
                if rate_enable:
                    div = 100000
                    rate = round(total / entity_pop * div, 4)
                    curr_value = rate
                else:
                    curr_value = total
                    
                # Save data in memory
                gr_data.loc[len(gr_data)] = [entity, year, period, curr_value]
                temp_df.loc[len(temp_df)] = [year, period, curr_value]
        
        # Calculate variation coefficient
        all_values = list(temp_df[temp_df['year'] < max_year]['value'])
        var_coef = round(100.0 * ss.variation(all_values ), 4)
        
        # Calculate stats
        for period in range(1, 14):
            
            # Calculate percentage variation by years
            perc_var_list = []
            for year in range(max_year, max_year - 5, -1):
                n1_values = list(temp_df[(temp_df['period'] == period) & (temp_df['year'] == year)]['value'])
                n2_values = list(temp_df[(temp_df['period'] == period) & (temp_df['year'] == (year - 1))]['value'])
                perc_var = 0
                
                if len(n1_values) and len(n2_values):
                    n1_value = n1_values[0]
                    n2_value = n2_values[0]
                    if n1_value > 0 and n2_value > 0:
                        perc_var = (n1_value - n2_value) / n2_value
                
                perc_var_list.append(perc_var)
                
            # Percentage variations local variables
            pv_period = str(max_year) + '-' + str(max_year - 1)
            pv_value = 0
            pv_min_lim = 0
            pv_max_lim = 0
            if len(perc_var_list) == 5:
                pv_value = round(perc_var_list[0], 4)
                pv_min_lim = round(min(perc_var_list[1:]), 4)
                pv_max_lim = round(max(perc_var_list[1:]), 4)
            
            # Filter data by period
            values = temp_df[(temp_df['period'] == period) & (temp_df['year'] < max_year)]['value']
            values = [x for x in values if x > 0]
            
            # Entity-period vars
            total = 0
            mean = 0
            stdev = 0
            min_value = 0
            max_value = 0
            p25 = 0
            p50 = 0
            p75 = 0
            
            # Not taking into account current year
            no_data = n_rows - len(values) - 1
            
            if len(values) > 0:
                values.sort()
                
                # Calc stats
                total = round(sum(values), 4)
                mean = round(np.mean(values), 4)
                stdev = round(np.std(values), 4)
                min_value = round(min(values), 4)
                max_value = round(max(values), 4)
                p25 = round(np.percentile(values, 25), 4)
                p50 = round(np.percentile(values, 50), 4)
                p75 = round(np.percentile(values, 75), 4)
            
            # Save row item
            row_item = {'entity': entity, 'period': period, 'total': total, 'mean': mean, 'stdev': stdev, 'min': min_value, 
                        'p25': p25, 'p50':p50, 'p75': p75, 'max': max_value, 'no_data': no_data, 'var_coef': var_coef,
                        'pv_period': pv_period, 'pv_value': pv_value, 'pv_min_lim': pv_min_lim, 'pv_max_lim': pv_max_lim}
            stats_data = stats_data.append(row_item, ignore_index=True)
    
    # Return result datasets
    return gr_data, stats_data

# Core function - Save to CSV file the result stats by entity
def save_results(curr_event, df, exec_date, file_name):
    exec_col = 'exec_date'
    
    # Save model data results
    if df is not None and len(df):
        
        # Post processing of the data
        df.reset_index(inplace=True)
        df.insert(0, exec_col, str(exec_date))
        
        # Persist data
        filename = '../result/' + curr_event + '/' + file_name + '.csv'
        ul.save_df_to_csv_file(filename, df, False)

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
            data_list = get_data_by_entity(filename, entity_filter, curr_event['frequency'])
            
            # 5. Get population by entity and year
            pop_data = get_population_by_entity()
            
            # 6. Calculate descriptive stats
            logging.info(' = Calculate descriptive stats - ' + str(datetime.now()))
            exec_date = datetime.now()
            rate_enable = curr_event['rate_enable']
            max_year = 2020
            gr_data, stats_data = calc_desc_stats(data_list, pop_data, rate_enable, max_year)
            
            # 7. Save grouped data by entity
            logging.info(' = Save grouped data by entity - ' + str(datetime.now()))
            save_results(event_name, gr_data, exec_date, 'raw_data')
            
            # 8. Save stats results by entity
            logging.info(' = Save stats results by entity - ' + str(datetime.now()))
            save_results(event_name, stats_data, exec_date, 'result_data')
    
    logging.info(">> END PROGRAM: " + str(datetime.now()))
    logging.shutdown()
#####################
#### END PROGRAM ####
#####################
