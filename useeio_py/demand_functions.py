# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype


'''
# TRANSLATE:

# Functions for assembling final demand vectors

#'Registry of functions that construct various demand vector in the form of as a named list with nested names
#'as keys and function name as values
DemandVectorFunctionRegistry <- list()
# Production
DemandVectorFunctionRegistry$Production$Complete <- "prepareProductionDemand"
DemandVectorFunctionRegistry$Production$Domestic <- "prepareDomesticProductionDemand"
# Consumption
DemandVectorFunctionRegistry$Consumption$Complete <- "prepareConsumptionDemand"
DemandVectorFunctionRegistry$Consumption$Domestic <- "prepareDomesticConsumptionDemand"
DemandVectorFunctionRegistry$Consumption$Household <- "prepareHouseholdDemand"
'''

def sum_demand_cols(Y, codes):
    '''
    #' Sums across sectors for a given set of codes/cols in a given final demand df
    #' @param Y, a model Demand df 
    #' @param codes, sector code(s) for a subset of Final Demand cols
    #' @return A named vector with model sectors and demand amounts
    # 
    '''
    logging.debug("Function not implemented")
    sys.exit()

def sum_for_consumption(model, Y):
    '''
    #' Sums the demand cols representing final consumption, i.e. household, investment, and government
    #' Complete national consumption formula: y_c <-  Y_h + Y_v + Y_g 
    #' Domestic portion of national consumption: y_dc <- Y_dh + Y_dv + Y_dg
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @param Y, a model Demand df.
    #' @return A named vector with model sectors and demand amounts
    '''
    logging.debug("Function not implemented")
    sys.exit()

def prepare_production_demand(model):
    '''
    #' Prepares a demand vector representing production
    #' Formula for production vector: y_p <- y_c + y_e + y_m + y_delta
    #' where y_c = consumption, y_e = exports, y_m = imports, y_delta = change in inventories
    #' y_m values are generally negative in the BEA data and thus are added (whereas when positive they are subtracted)
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return A named vector with demand
    '''
    logging.debug("Function not implemented")
    sys.exit()

def prepare_domestic_production_demand(model):
    '''
    #' Prepares a demand vector representing domestic production
    #' Formula for production vector: y_p <- y_dc + y_e + y_d_delta + mu
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return A named vector with demand
    '''
    logging.debug("Function not implemented")
    sys.exit()

def prepare_consumption_demand(model):
    '''
    #' Prepares a demand vector representing consumption
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return a named vector with demand
    '''
    logging.debug("Function not implemented")
    sys.exit()

def prepare_domestic_consumption_demand(model):
    '''
    #' Prepares a demand vector representing domestic consumption
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return A named vector with demand
    '''
    logging.debug("Function not implemented")
    sys.exit()

def prepare_household_demand(model):
    '''
    #' Prepares a demand vector representing household consumption
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return A named vector with demand
    '''
    logging.debug("Function not implemented")
    sys.exit()

def is_demand_vector_valid(dv, L):
    '''
    A function to validate a user provided demand vector

    Arguments:
    dv: a user provided demand vector
    L:  the L matrix for the given model, used as a reference

    return: A logical value indicating demand vector is valid or not.
    '''
    # dv index shoud be part of sectors in L
    is_valid = all([is_numeric_dtype(dv.iloc[:,0]), set(dv.index).issubset(L.index)])
    return(is_valid)

def format_demand_vector(dv, L):
    '''
    Format a named demand vector with partial sectors to have all the rows and ordering needed

    Arguments:
    dv: a user provided demand vector. See calculateEEIOModel()
    L:  the L matrix for the given model, used as a reference

    return: A DataFrame with values for all names in L, and ordered like L
    '''
    # create zero demand vector with row for each columns in L and update rows with matching index in user-specified dv
    a = np.zeros(shape=(L.shape[0], 1))
    d = pd.DataFrame(a, index=L.index)

    # ensure column and index names match so new DataFrame is properly updated.
    d.columns = [0]
    dv.columns = [0]
    d.index.rename('', inplace=True)
    dv.index.rename('', inplace=True)

    d.update(dv)
    return(d)

def extract_and_format_demand_vector(file_path, demand_name, model):
    '''
    #' Read demand vector from a csv file and format for use in model calculations
    #' @param file_path str, path to csv file containing demand data
    #' @param demand_name str, name of demand data as field header
    #' @param model, a model
    #' @return a demand vector formatted for use in calculating model results
    #' @export
    '''
    logging.debug("Function not implemented")
    sys.exit()
