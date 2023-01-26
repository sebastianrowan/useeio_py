# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from classes import Model

#TODO: Most or all of these functions can probably be wrapped into methods inside the Model class and called on __init__()

def build_model(model_name, config_paths = None):
    '''
    Build an EEIO model.

    Keyword arguments:
    model_name:     Name of the model from a config file.
    config_paths:   str list, paths (including file name) of model configuration file
                    and optional agg/disagg configuration file(s).
                    If NULL, built-in config files are used.

    return: An EEIO model instance with complete components and attributes
    #' @export
    '''
    #TODO: add these functions as methods in the model class.
    model = Model(model_name, config_paths)
    model.load_io_data()
    model.load_and_build_satellite_tables()
    model.load_and_build_indicators()
    model.load_demand_vectors()
    model.construct_EEIO_matrices()
    # model = initialize_model(model_name, config_paths) #DONE
    # model = load_io_data(model, config_paths)
    # model = load_and_build_satellite_tables(model)
    # model = load_and_build_indicators(model)
    # model = load_demand_vectors(model)
    # model = construct_EEIO_matrices(model)
    return(model)

def construct_EEIO_matrices(model):
    '''
    Construct EEIO matrices based on loaded IO tables, built satellite tables,
    and indicator tables.

    Keyword arguments:
    model:  An EEIO model object with model specs, IO tables, satellite tables, and indicators loaded
    
    return: An EEIO model with EEIO matrices loaded.
    '''
    pass

def create_B_from_flow_data_and_output(model):
    '''
    #'Creates the B matrix from the flow data
    #'@param model, a model with econ and flow data loaded
    #'@return B, a matrix in flow x sector format with values of flow per $ output sector
    '''
    pass

def generate_cbs_from_tbs_and_model(model):
    '''
    #' Prepare coefficients (x unit/$) from the totals by flow and sector (x unit)
    #' @param model An EEIO model object with model specs, IO tables, satellite tables, and indicators loaded
    #' @return A dataframe of Coefficients-by-Sector (CbS) table
    '''
    pass

def standardize_and_cast_satellite_table(df, model):
    '''
    #' Converts flows table into flows x sector matrix-like format
    #' @param df a dataframe of flowables, contexts, units, sectors and locations
    #' @param model An EEIO model object with model specs, IO tables, satellite tables, and indicators loaded
    #' @return A matrix-like dataframe of flows x sector 
    '''
    pass

def create_C_from_factors_and_B_flows(factors, B_flows):
    '''
    #' Generate C matrix from indicator factors and a model B matrix
    #' @param factors df in model$Indicators$factors format
    #' @param B_flows Flows from B matrix to use for reference
    #' @return C, a matrix in indicator x flow format
    '''
    pass