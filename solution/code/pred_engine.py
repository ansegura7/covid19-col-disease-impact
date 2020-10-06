# -*- coding: utf-8 -*-
"""
    Created by: Andres Segura Tinoco
    Version: 1.1.0
    Created on: Sep 09, 2020
    Updated on: Oct 06, 2020
    Description: Predictive engine for both scenarios (partial or w/o COVID and full or w COVID)..
"""

# Import Python 
import os
import logging
import pandas as pd
import numpy as np
import scipy.stats as ss
import itertools
import timeit
from datetime import datetime
from math import ceil
from warnings import filterwarnings

# Import custom libraries
import util_lib as ul

# Import Time Series libraries
import statsmodels.api as sm