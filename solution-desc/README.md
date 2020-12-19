# Impact of Covid-19 in Colombia: Descriptive Engine
Descriptive solution for the development and evaluation of mathematical and epidemiological models that support decision-making in response to the Covid-19 emergency in Colombia.

## Requirements
The solution can be run on both a Linux and Windows operating system. Python 3.7.x or later is required to run the solution. It can also be run on the latest version of Anaconda.

## Libraries
The Python libraries needed to run the solution are:

```python
import os
import json
import yaml
import logging
import pandas as pd
import numpy as np
import scipy.stats as ss
import util_lib as ul
from datetime import datetime
from math import sqrt, log
from scipy import stats
from sklearn.metrics import mean_squared_error
```

## Program setup
The behavior of the predictive engine is configured from an input JSON file.

```json
{
  "event_list": [
    {
      "enabled": true,
      "frequency": "weekly",
      "name": "TUBERCULOSIS",
      "rate_enable": true,
      "skip_years": []
    },
    {
      ...
    }
  ],
  "entity_filter": []
}
```

## Author
- Created by <a href="https://github.com/ansegura7">Andrés Segura Tinoco</a>
- Created on Nov 15, 2020
- Last update on Dec 16, 2020
