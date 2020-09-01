# -*- coding: utf-8 -*-
"""
    Created By: Andres Segura Tinoco
    Created On: Aug 10, 2020
    Version: 1.0.0
    Description: ETL Process
"""

# Database libraries
import pyodbc

# Import util libraries
import yaml
import csv
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
def get_full_data(indicator):
    full_data = []
    url_file = '../' + indicator + '/data/raw_data.csv'
    
    raw_data = read_csv_file(url_file)
    
    for row in raw_data[1:]:
        week = 1
        for item in row[5:]:
            if item.isnumeric():
                full_data.append(row[:5] + [week, item])
                week += 1
            else:
                break
    
    return full_data

def db_save_data(db_login, data_list):
    
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
        query = '''
                    INSERT INTO [dbo].[indicator_data]
                           ([indicator],[sub_indicator],[entity],[department],[year],[week],[value])
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
indicator = '3-tuberculosis'
data = get_full_data(indicator)

# 3. Save data into DB
db_save_data(db_login, data)

print(">> END PROGRAM: " + str(datetime.now()))
#####################
#### End Program ####
#####################
