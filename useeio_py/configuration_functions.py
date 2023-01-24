# -*- coding: utf-8 -*-

'''
Handle configuration files
'''
import pandas as pd
import numpy as np

def get_configuration(config_name, config_type, config_paths = None):
    '''
    Gets a stored or user specified model or aggregation/disaggregation configuration file

    Keyword arguments:

    config_name:    str, name of the configuration file
    config_type:    str, configuration type, can be "model", "disagg", or "agg"
    config_paths:   str list, paths (including file name) of model configuration file
                    and optional agg/disagg configuration file(s). 
                    If NULL, built-in config files are used.

    return: A list of model specifications.
    '''
    config_file = f"{config_name}.yml"
    pass

def see_available_models():
    '''
    Show model names with configuration files

    return: Prints model names
    '''
    config_files = find_model_configuration_files()
    model_names = config_files[0:(len(config_files) - 4)]
    print(model_names)

def find_model_configuration_files():
    '''
    Get model config files

    return: list of model config files
    '''
    pass