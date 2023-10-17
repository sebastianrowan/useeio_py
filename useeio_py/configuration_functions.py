# -*- coding: utf-8 -*-

'''
Handle configuration files
'''
import pandas as pd
import numpy as np
import pkgutil
import os.path
import yaml

def get_configuration(config_name, config_type, config_paths = None):
    '''
    Gets a stored or user specified model or aggregation/disaggregation configuration file

    Arguments:

    config_name:    str, name of the configuration file
    config_type:    str, configuration type, can be "model", "disagg", or "agg"
    config_paths:   str list, paths (including file name) of model configuration file
                    and optional agg/disagg configuration file(s). 
                    If NULL, built-in config files are used.

    return: A dictionary of model specifications.
    '''
    config_file = f"{config_name}.yml"
    if config_paths is None:
        config_path = f"inst/extdata/{config_type}specs/{config_file}"
        config = pkgutil.get_data(__name__,config_path)
        config = yaml.safe_load(config)
    else:
        config_path = list(filter(lambda path: path.endswith(config_file), config_paths))[0] #TODO: if config_paths is a list that includes agg/disagg confs, how to get right one?
        try:
            with open(config_path, 'r') as conf:
                config = yaml.safe_load(conf)
        except:
            print(f"{config_file} must be available in {os.path.dirname(config_path)}")
    
    return(config)



def see_available_models():
    '''
    Show model names with configuration files

    return: Prints model names
    '''
    logging.debug("Function not implemented")
    sys.exit()
    '''
    config_files = find_model_configuration_files()
    model_names = #TODO: remove ".yml" from end of each string
    print(model_names)
    '''

def find_model_configuration_files():
    '''
    Get model config files

    return: list of model config files
    '''
    logging.debug("Function not implemented")
    sys.exit()