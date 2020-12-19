# Impact of Covid-19 in Colombia: Predictive Engine
Predictive (or forecast) solution for the development and evaluation of mathematical and epidemiological models that support decision-making in response to the Covid-19 emergency in Colombia.

## Requirements
The solution can be run on both a Linux and Windows operating system. Python 3.7.x or later is required to run the solution. It can also be run on the latest version of Anaconda.

## Libraries
The Python libraries needed to run the solution are:

```python
import concurrent.futures
import json
import logging
import numpy as np
import os
import pandas as pd
import pred_engine as pe
import scipy.stats as ss
import statsmodels.api as sm
import timeit
import util_lib as ul
import yaml
from datetime import datetime
from joblib import Parallel
from joblib import delayed
from math import ceil
from math import sqrt, log
from multiprocessing import cpu_count
from scipy import stats
from sklearn.metrics import mean_squared_error
from warnings import filterwarnings
```

## Program setup
The behavior of the predictive engine is configured from an input JSON file.

```json
{
  "event_list": [
    {
      "analysis_list": [ "PARTIAL", "FULL" ],
      "ci_alpha": 0.9,
      "enabled": true,
      "full_init_date": "2017-01-01",
      "mape_threshold": 4.0,
      "n_forecast": 13,
      "name": "TUBERCULOSIS",
      "partial_end_date": "2019-12-27",
      "perc_test": 0.20,
      "ts_tolerance": 4.0
    },
    {
      ...
    }
  ],
  "entity_filter": ["COLOMBIA", "BOGOTA DC", "ANTIOQUIA"],
  "n_process": 1
}
```

## Author
- Created by <a href="https://github.com/ansegura7">Andrés Segura Tinoco</a>
- Created on Jul 25, 2020
- Last update on Dec 08, 2020
