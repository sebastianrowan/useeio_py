from context import (
    USEEIOModel, 
    load_io_tables,
    io_functions
    )
import pandas as pd
import importlib.resources
import inspect
import seaborn as sns
import numpy as np
import logging
# logging.basicConfig(level=logging.DEBUG)

# path = "C:/GitHub/useeio_py/useeio_py/data2/Sector_IndustryCodeName_2012.parquet"
# x = pd.read_parquet(path)

# print(x.head())
# print(x.columns)

'''
Currently working from:
    useeio_model.py >>> __init__() >>> load_io_tables.load_io_data()
    >>> load_io_tables.load_io_data() >>> aggregate_functions.aggregate_model()
        >>> aggregate_va()
        >>> aggregate_use_table()
        >>> aggregate_sector()
'''

# model = USEEIOModel('USEEIOv2.1-422')


iris = sns.load_dataset("iris").head()

print(iris.iloc[1,:])
print(iris.iloc[-1,:])
# a = "sepal_length"
# b = ["sepal_width", "petal_length"]

# x = iris.loc[b]
# y = ~iris.loc[b]

# print(x)
# print(y)

# c = ["sepal_length", "sepal_width", "petal_length", "petal_width"]


# x = iris.iloc[0:4,0:4]
# x.index = x.columns

# x = x.drop(["show", "sepal_length"], axis=1, errors = "ignore")
# print(x)