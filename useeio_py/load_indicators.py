# -*- coding: utf-8 -*-
'''Functions for loading and checking indicator data'''

import pandas as pd
import numpy as np


def load_and_build_indicators(model):
    '''
    #' Loads data for all model indicators as listed in model specs
    #' @param model A model object with model specs, IO tables, and satelilte tables loaded
    #' @return A model object with Indicators added
    '''
    # Load model indicators
    indicators = load_indicators(model)

    # Add to model object
    model.Indicators = indicators
    return(model)

def load_indicators(model):
    '''
    #' Load indicators and associated factors in a list based on model config.
    #' @param model A model object with model specs, IO tables, and satellite tables loaded.
    #' @return A list with a dataframe for indicator meta and a dataframe for indicator factors.
    '''
    logging.debug("Function not implemented")
    sys.exit()
    '''
    logging::loginfo("Initializing model indicators...")
    meta <- data.frame()
    factors <- data.frame()
    for (s in model$specs$Indicators) {
        logging::loginfo(paste0("Getting ", s$Name, " indicator from ", s$FileLocation, "..."))
        
        # Populate metadata
        meta_fields <- c("Name","Code","Group","Unit","SimpleUnit","SimpleName")
        i <- s[meta_fields]
        meta <- rbind(meta,data.frame(i, stringsAsFactors = FALSE))

        #Get factors
        f <- loadFactors(s)
        #Make sure indicator name comes from spec and not factor source data
        f$Indicator <- s[["Name"]]
        factors <- rbind(factors,f)
        checkIndicatorforFlows(f, model$SatelliteTables$flows)
    }   
    indicators <- list(meta=meta,factors=factors)
    return(indicators)
    '''

def load_factors(ind_spec):
    '''
    #' Load indicator factors based on spec from static or dynamic source
    #' @param ind_spec Specification of an indicator
    #' @return A dataframe of factors with factor_fields
    '''
    logging.debug("Function not implemented")
    sys.exit()
    '''
    if(is.null(ind_spec$ScriptFunctionCall)) {
        # Load static LCIA factors from useeio respository data
        StaticIndicatorFactors <- loadLCIAfactors()
        # Subset LCIA factors list for the abbreviations
        factors <- StaticIndicatorFactors[StaticIndicatorFactors$Code == ind_spec$Code, ]
        # Add Indicator column
        factors <- cbind("Indicator" = ind_spec$Name, factors)
    } else {
        func_to_eval <- ind_spec$ScriptFunctionCall
        indloadfunction <- as.name(func_to_eval)
        factors <- do.call(eval(indloadfunction), list(ind_spec))
        factors <- prepareLCIAmethodforIndicators(factors)
    }
    factor_fields <- c("Indicator","Flowable","Context","Unit","Amount")
    factors <- factors[,factor_fields]
    return(factors)
    '''

def load_lcia_factors():
    '''
    #' Loads all LCIA factors from static source file after melting it to long file
    #' @return A dataframe of LCIA factors.
    '''
    logging.debug("Function not implemented")
    sys.exit()
    '''
    # Load static LCIA factors
    lciafact <- utils::read.table(system.file("extdata", "USEEIO_LCIA_Factors.csv", package = "useeior"),
                                    sep = ",", header = TRUE, stringsAsFactors = FALSE, check.names = FALSE)
    # Melt these so there is one indicator score per line
    lciafactlong <- reshape2::melt(lciafact, id.vars = c("Flowable", "Context", "Unit", "UUID"))
    # Add Code and Amount
    lciafactlong[, "Code"] <- as.character(lciafactlong$variable)
    lciafactlong[, "Amount"] <- as.numeric(lciafactlong$value)
    # Drop zeroes and keep wanted columns
    lciafactlong <- lciafactlong[lciafactlong$value>0,
                                    c("Flowable", "UUID", "Context", "Unit", "Amount", "Code")]
    return(lciafactlong)
    '''

def check_indicator_for_flows(factors, flows):
    '''
    #' Checks an LCIA indicator to ensure that flows exist in the model for that indicator
    #' @param factors A dataframe of indicator characterization factors
    #' @param flows A dataframe of flows from model SatelliteTables
    '''
    logging.debug("Function not implemented")
    sys.exit()
    '''
    if(is.null(flows)){
        logging::logwarn("No flows found in model")
        return()
    }
    
    factor_list <- apply(cbind(factors['Context'], factors['Flowable']), 1, FUN = joinStringswithSlashes)
    flows_list <- apply(cbind(flows['Context'], flows['Flowable']), 1, FUN = joinStringswithSlashes)
    if(length(intersect(factor_list,flows_list)) == 0){
        logging::logwarn("No flows found for this indicator in model")
    }
    '''


