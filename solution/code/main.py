# -*- coding: utf-8 -*-
"""
    Created By: Andres Segura Tinoco
    Created On: Sep 09, 2020
    Version: 1.0.0
    Description: Main class of the solution.
"""

# Import list
import pandas as pd
from datetime import datetime

######################
### UTIL FUNCTIONS ###
######################

# Util function - Read the CSV dataset and convert it to a dictionary by entity
def get_data_by_entity():
    data_list = dict()
    
    # Read data from CSV dataset
    filename = '../data/dataset.csv'
    raw_data = pd.read_csv(filename)
    
    # Filter data by entity
    if len(raw_data):
        entity_list = raw_data['entity'].unique()
        for entity in entity_list:
            entity_data = raw_data[raw_data['entity'] == entity]
            data_list[entity] = entity_data
    
    return data_list

#####################
### Start Program ###
#####################
print('>> START PROGRAM: ' + str(datetime.now()))

# 1. Get list of datasets by entities
data_list = get_data_by_entity()

print('>> END PROGRAM: ' + str(datetime.now()))
#####################
#### End Program ####
#####################
