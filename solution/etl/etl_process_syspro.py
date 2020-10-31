# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.0.0
    Created on: Oct 14, 2020
    Updated on: Oct 30, 2020
    Description: ETL Process (SYSPRO)
"""

# Database libraries
import pyodbc

# Import util libraries
import yaml
import csv
import pandas as pd
from datetime import datetime

# Util function - Read dict from yaml file
def get_dict_from_yaml(yaml_path):
    result = dict()
    
    with open(yaml_path) as f:
        yaml_file = f.read()
        result = yaml.load(yaml_file, Loader=yaml.FullLoader)
    
    return result

# DB function - Get database credentials
def get_db_credentials():
    yaml_path = 'config/database.yml'
    db_login = get_dict_from_yaml(yaml_path)
    return db_login

# Util function - Read CSV file from full filepath
def read_csv_file(filename, encoding='utf-8', delimiter=','):
    data = []
    
    with open(filename, 'r', encoding=encoding) as f:
        csv_file = csv.reader(f, delimiter=delimiter)
        for row in csv_file:
            if row:
                data.append(row)
            
    return data

# Get data from CSV file
def get_full_data(var_column, entity_type, zero=0):
    full_data = []
    url_entity = 'config/divipola.csv'
    url_data = 'data/raw_data_syspro.csv'
    
    # Reading entity list
    df_entities = pd.read_csv(url_entity)
    entity_list = df_entities[df_entities['type'] == entity_type]['entity'].unique()
    print(' = N valid entities:', len(entity_list))
    
    # Reading data from file
    raw_data = read_csv_file(url_data, encoding='utf-8-sig')
    
    # Grouping data
    if len(raw_data) > 1:
        df = pd.DataFrame.from_records(raw_data[1:], columns=raw_data[0])
        df['date'] = pd.to_datetime(df['date'])
        df['week'] = df['week'].astype(int)
        df[var_column] = df[var_column].astype(int)

        # Validate year-week pairs        
        for ix, row in df.iterrows():
            curr_date = row['date']
            curr_week = int(row['week'])
            
            if curr_week < 53:
                df.at[ix, 'year'] = curr_date.year
            else:
                df.at[ix, 'year'] = curr_date.year + 1
                df.at[ix, 'week'] = 1
        
        # Remove non-relevant fields
        if entity_type == 'department':
            gr_data = df.drop(columns=['chapter', 'group', 'sub_group', 'diagnosis', 'cod', 'com', 'municipality', 'event_type'])
            df_col_entity = 'department'
        else:
            gr_data = df.drop(columns=['chapter', 'group', 'sub_group', 'diagnosis', 'cod', 'com', 'department', 'event_type'])
            df_col_entity = 'municipality'
            
        # Remove non-relevant rows
        index_id = gr_data[~gr_data[df_col_entity].isin(entity_list)].index 
        gr_data.drop(index_id, inplace=True)
        
        # Grouping data by entity-year-week
        gr_data = gr_data.groupby(['event', 'sub_event', df_col_entity, 'year', 'week']).agg({var_column:'sum'})
        gr_data.reset_index(inplace=True)
        gr_data = gr_data.sort_values(by=[df_col_entity, 'year', 'week'], ascending=True)
        
        # Complete data with zero input param
        if len(gr_data):
            #entity_list = gr_data[df_col_entity].unique()
            year_list = [2017, 2018, 2019, 2020]
            week_list = [week for week in range(1, 53)]
            
            # Filtering and grouping data by entity
            for entity in entity_list:
                entity_data = gr_data[gr_data[df_col_entity] == entity]
                
                for year in year_list:
                    for week in week_list:
                        if year < 2020 or week < 17:
                            if len(entity_data[(entity_data['year'] == year) & (entity_data['week'] == week)]) == 0:
                                gr_data.loc[len(gr_data)] = ['DM', 'DIABETES MELLITUS', entity, year, week, zero]
            
            # Show results
            print('>> Total rows:', len(gr_data))
            for entity in entity_list:
            	entity_data = gr_data[gr_data[df_col_entity] == entity]
            	print(' - Entity:', entity, ', rows:', len(entity_data))
        
        # Save and sort temp data
        temp_data = gr_data
        temp_data['entity'] = temp_data[df_col_entity]
        temp_data = temp_data.reindex(columns=['event', 'sub_event', 'entity', df_col_entity, 'year', 'week', var_column])
        temp_data = temp_data.sort_values(by=[df_col_entity, 'year', 'week'], ascending=True)
        
        # Final conversion: from dataframe to array list
        for ix, row in temp_data.iterrows():
            full_data.append([row['event'], row['sub_event'], row['entity'], row[df_col_entity], row['year'], row['week'], row[var_column]])
        
    # Return data
    return full_data

# Save data to database
def db_save_data(db_login, data_list, entity_type):
    
    if len(data_list) == 0:
        print(' - No data to save')
        return
    else:
        print(' - Start of bulk insert for', len(data_list))
    
    # Get database connection
    cnxn = pyodbc.connect(driver=db_login['driver'], server=db_login['server'], database=db_login['database'], trusted_connection=db_login['trusted_connection'])
    
    try:
        cursor = cnxn.cursor()
        
        # Insert many rows
        query = ''
        if entity_type == 'capital':
            query = '''
                        INSERT INTO [dbo].[events_data_by_capital]
                               ([event],[sub_event],[capital],[department],[year],[week],[value])
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                    '''
        else:
            query = '''
                        INSERT INTO [dbo].[events_data]
                               ([event],[sub_event],[entity],[department],[year],[week],[value])
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                    '''
        
        cnxn.autocommit = False
        cursor.fast_executemany = True
        cursor.executemany(query, data_list)
        
    except pyodbc.DatabaseError as e:
        cnxn.rollback()
        print(' - Pyodbc error: ' + str(e))
    else:
        cnxn.commit()
        print(' - Data stored in the database for', len(data_list))
    finally:
        cnxn.autocommit = True
        cursor.close()
    
    print(' - End of bulk insert: ' + str(datetime.now()))

#####################
### START PROGRAM ###
#####################
if __name__ == "__main__":
    print(">> START PROGRAM: " + str(datetime.now()))
    var_column = 'rips_num_attentions'
    entity_type = 'department' # or capital
    zero = -1
    
    # 1. Get database credentials
    db_login = get_db_credentials()
    
    # 2. Get data from CSV file
    data = get_full_data(var_column, entity_type, zero)
    
    # 3. Save data into DB
    db_save_data(db_login, data, entity_type)
    
    print(">> END PROGRAM: " + str(datetime.now()))
#####################
#### End Program ####
#####################
