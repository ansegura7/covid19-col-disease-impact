# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.0.0
    Created on: Nov 23, 2020
    Updated on: Nov 23, 2020
    Description: Main class of the descriptive-engine solution.
"""

# Import Python
import logging
from datetime import datetime

######################
### CORE FUNCTIONS ###
######################



#####################
### START PROGRAM ###
#####################
if __name__ == "__main__":
    
    # 0. Program variables
    log_path = 'log/log_file.log'
    yaml_path = 'config/config.yml'
    logging.basicConfig(filename=log_path, level=logging.INFO)
    logging.info('>> START PROGRAM: ' + str(datetime.now()))
    
    logging.info(">> END PROGRAM: " + str(datetime.now()))
    logging.shutdown()
#####################
#### END PROGRAM ####
#####################
