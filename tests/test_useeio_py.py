from context import Model
from pprint import pprint
import pandas as pd
import importlib.resources
import inspect

model = Model('USEEIOv2.0')
model.load_io_data()

print(model.MarginSectors.head())