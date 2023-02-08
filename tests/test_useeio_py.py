from context import (
    USEEIOModel, 
    load_io_tables,
    io_functions,
    get_state_name_from_abb
    )
import pandas as pd
import importlib.resources
import inspect
import seaborn as sbn
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)


model = USEEIOModel('USEEIOv2.0')

df1 = pd.DataFrame(
    {
        'name': ['sam', 'bob', 'joe'],
        'age': [23, 24, 25],
        'uni': ['unh', 'unh', 'uvm']
    }
)

df2 = pd.DataFrame(
    {
        'uni_name':['unh','uvm'],
        'pop': [10_000, 8_000],
        'cost': [45_000, 55_000]
    }
)

df3 = df1.merge(
    df2, 
    how='left',
    left_on='uni',
    right_on='uni_name'
)
print(df3.columns)