# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.0.0
    Created on: Oct 14, 2020
    Updated on: Oct 14, 2020
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
def get_full_data():
    full_data = []
    url_file = 'data/raw_data_syspro.csv'
    
    raw_data = read_csv_file(url_file)
    
    if len(raw_data) > 1:
        df = pd.DataFrame.from_records(raw_data[1:], columns=raw_data[0])
        df['date'] = pd.to_datetime(df['date'])
        for ix, row in df.iterrows():
            curr_date = row['date']
            df.at[ix, 'date'] = curr_date.year
            df.at[ix, 'week'] = curr_date.strftime("%U")
        
        full_data = df
        
    return full_data

# Save data to database
def db_save_data(db_login, data_list, save_type):
    
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
        if save_type == 'CAPITAL':
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
### Start Program ###
#####################
print(">> START PROGRAM: " + str(datetime.now()))

# 1. Get database credentials
db_login = get_db_credentials()

# 2. Get data from CSV file
data = get_full_data()

# 3. Save data into DB
save_type = ''
#db_save_data(db_login, data, save_type )

print(">> END PROGRAM: " + str(datetime.now()))
#####################
#### End Program ####
#####################
