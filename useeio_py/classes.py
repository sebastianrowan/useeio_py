# -*- coding: utf-8 -*-

import importlib.resources
import os.path
import pyarrow.parquet as pq
import pandas as pd
import re
import inspect
from .configuration_functions import get_configuration
from .utility_functions import get_vector_of_codes, stack
from . import load_io_tables
from . import load_satellites


class Model:
    
    def __init__(self, model_name, config_paths = None):
        '''
        Initialize model with specifications and fundamental crosswalk table.

        Keyword arguments:
        modelname:      Name of the model from a config file.
        configpaths:    str list, paths (including file name) of model configuration file
                        and optional agg/disagg configuration file(s).
                        If None, built-in config files are used.
        '''
        print("begin model initialization...")
        self._valid = True
        self._invalid_reason = None
        # Get model specs
        self.specs = get_configuration(model_name, "model", config_paths)

        if self.specs is None:
            self._valid = False
            self._invalid_reason = f"No configuration exists for a model named {model_name}"
        else:
            # Get model crosswalk
            crosswalk_name = f"MasterCrosswalk{self.specs['BaseIOSchema']}.parquet"
            crosswalk_parquet = importlib.resources.files('useeio_py.data').joinpath(crosswalk_name)
            crosswalk = pd.read_parquet(crosswalk_parquet)
            cols = ["NAICS_2012_Code"] + list((crosswalk.filter(regex = "^BEA", axis=1).columns))
            crosswalk = crosswalk[cols]
            crosswalk = crosswalk.drop_duplicates()
            crosswalk = crosswalk.rename(
                columns = lambda x: re.sub(
                    f"_{self.specs['BaseIOSchema']}|_Code",
                    "", x))
            # Assign initial model crosswalk based on base schema
            model_schema = "USEEIO"
            base_schema = f"BEA_{self.specs['BaseIOLevel']}"
            crosswalk[model_schema] = crosswalk[base_schema]
            self.crosswalk = crosswalk

    load_io_tables.load_io_data(self)  
    load_satellites.load_and_build_satellite_tables(self)


    