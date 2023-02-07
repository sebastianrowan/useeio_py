# -*- coding: utf-8 -*-
'''Functions for loading gross output and chain-type price indices'''

import pandas as pd
import numpy as np
import logging
import importlib.resources


def load_national_gross_output_table(specs):
    '''
    Load US Gross Output table based on model specifications.
    
    Argument:
    specs:  Specifications of the model.
    
    return: A data.frame of US Gross Output.
    '''
    pass
    '''
    logging::loginfo("Initializing Gross Output tables...")
    # Load pre-saved Gross Output tables
    GrossOutput <- get(paste0(specs$BaseIOLevel, "_GrossOutput_IO")) * 1E6 # data frame, values are in dollars ($)
    return(GrossOutput)
    '''

#TODO: test implementation
def load_chain_price_index_table(specs):
    '''
    #' Load Chain Price Index table based on model specifications.
    #' @param specs Specifications of the model.
    #' @return A data.frame of Chain Price Index.
    '''
    logging.info("Initializing Chain Price Index tables...")
    chain_price_index = pd.read_parquet(importlib.resources.files('useeio_py.data2').joinpath(
        f"{specs['BaseIOLevel']}_CPI_IO.parquet"
    ))
    return(chain_price_index)
    '''
    logging::loginfo("Initializing Chain Price Index tables...")
    ChainPriceIndex <- get(paste0(specs$BaseIOLevel, "_CPI_IO"))
    return(ChainPriceIndex)
    '''
