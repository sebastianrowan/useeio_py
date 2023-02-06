from context import (
    USEEIOModel, 
    load_io_tables,
    io_functions
    )
import pandas as pd
import importlib.resources
import inspect
import numpy as np

model = USEEIOModel('USEEIOv2.0')

io_codes = load_io_tables.load_io_codes(model)
bea = load_io_tables.load_national_io_data(
    model, io_codes
)
print(bea['DomesticFinalDemand'])