from context import USEEIOModel, load_io_tables
import pandas as pd
import importlib.resources
import inspect

model = USEEIOModel('USEEIOv2.0')

io_codes = load_io_tables.load_io_codes(model)
bea = load_io_tables.load_bea_tables(model.specs, io_codes)

print(len(bea))
