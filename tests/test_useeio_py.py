from context import USEEIOModel
import pandas as pd
import importlib.resources
import inspect

model = USEEIOModel('USEEIOv2.0')
model.load_io_data()