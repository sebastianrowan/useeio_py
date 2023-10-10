# -*- coding: utf-8 -*-
'''
Functions implementing core input-output analysis algorithms
'''
import sys
import logging
import importlib.resources
import pandas as pd
import numpy as np
from . import (utility_functions)

#TODO
def adjust_output_by_cpi(output_year, reference_year, location_acronym, is_ro_us, model, output_type):
    '''
    #' Adjust Industry output based on CPI.
    #' @param outputyear Year of Industry output.
    #' @param referenceyear Year of the currency reference.
    #' @param location_acronym Abbreviated location name of the model, e.g. "US" or "GA".
    #' @param IsRoUS A logical parameter indicating whether to adjust Industry output for Rest of US (RoUS).
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param output_type Type of the output, e.g. "Commodity" or "Industry"
    #' @return A dataframe contains adjusted Industry output with row names being BEA sector code.
    '''
    pass
    '''
    # Load Industry Gross Output
    selected_rows <- grepl(location_acronym, rownames(model$MultiYearIndustryOutput))
    Output <- cbind.data.frame(rownames(model$MultiYearIndustryOutput[selected_rows, ]),
                                model$MultiYearIndustryOutput[selected_rows, as.character(outputyear)])
    colnames(Output) <- c("SectorCode", "Output")
    # Adjust output based on CPI
    AdjustedOutput <- merge(Output, model[[paste0("MultiYear", output_type, "CPI")]][, as.character(c(referenceyear, outputyear))],
                            by.x = "SectorCode", by.y = 0)
    AdjustedOutput$DollarRatio <- AdjustedOutput[, as.character(referenceyear)]/AdjustedOutput[, as.character(outputyear)]
    AdjustedOutput[, paste(outputyear, "IndustryOutput", sep = "")] <- AdjustedOutput$Output * AdjustedOutput$DollarRatio
    # Assign rownames and keep wanted column
    rownames(AdjustedOutput) <- AdjustedOutput$SectorCode
    AdjustedOutput <- AdjustedOutput[rownames(model[[paste0("MultiYear", output_type, "CPI")]]),
                                    paste(outputyear, "IndustryOutput", sep = ""), drop = FALSE]
    return(AdjustedOutput)
    '''

#TODO: Test implementation
def normalize_io_transactions(io_transactions_df, io_output_df):
    '''
    Derive IO coefficients

    Arguments:
    IO_transactions_df: IO transactions of the model in dataframe format.
    IO_output_df: Output of the model in dataframe format.
    
    return: A matrix.
    '''
    Z = io_transactions_df.to_numpy()
    x = utility_functions.unlist(io_output_df)
    x_hat = np.diag(x)
    A = np.matmul(Z, np.linalg.inv(x_hat)) # R code: A <- Z %*% solve(x_hat)
    # R code: dimnames(A) <- dimnames(Z)
    return(A) # Not sure exactly how or if it is necessary to translate the dimnames line


#TODO
def generate_direct_requirements_from_use(model, domestic):
    '''
    #' Generate Direct Requirements matrix from Use table.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param domestic A logical parameter indicating whether to calculate DR or Domestic DR.
    #' @return Direct Requirements matrix of the model.
    '''
    pass
    '''
    # Generate direct requirements matrix (commodity x industry) from Use, see Miller and Blair section 5.1.1
    if (domestic==TRUE) {
        B <- normalizeIOTransactions(model$DomesticUseTransactions, model$IndustryOutput) # B = U %*% solve(x_hat)
    } else {
        B <- normalizeIOTransactions(model$UseTransactions, model$IndustryOutput) # B = U %*% solve(x_hat)
    }
    return(B)
    '''

#TODO: Test implementation
def generate_market_shares_from_make(model): 
    '''
    Generate Market Shares matrix from Make table.
    
    Argument:
    model:  A complete EEIO model: a list with USEEIO model components and attributes.
    
    return: Market Shares matrix of the model.
    '''
    # Generate market shares matrix (industry x commodity) from Make, see Miller and Blair section 5.3.1
    D = normalize_io_transactions(model.MakeTransactions, model.CommodityOutput) # D = V %*% solve(q_hat)
    # useeior comment: Put in code here for adjusting marketshares to remove scrap
    return(D)


#TODO: Test implementation
def generate_commodity_mix_matrix(model):
    '''
    Generate Commodity Mix matrix.

    Argument:
    model:  A complete EEIO model: a list with USEEIO model components and attributes.

    return: Commodity Mix matrix of the model.
    '''
    # Generate commodity mix matrix (commodity x industry), see Miller and Blair section 5.3.2
    C = normalize_io_transactions(np.T(model.MakeTransactions), model.IndustryOutput) # C = V' %*% solve(x_hat)
    industry_output_fractions = np.matrix.sum(C, axis = 1)
    err = utility_functions.unlist(abs(1-industry_output_fractions)>0.01)
    if sum(err) > 0:
        msg = "Error in commodity mix"
        logging.error(msg)
        sys.exit(msg)
    return(C)


#TODO
def transform_industry_output_to_commodity_output_for_year(year, model):
    '''
    #' Generate Commodity output by transforming Industry output using Commodity Mix matrix.
    #' @param year Year of Industry output
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @return A dataframe contains adjusted Commodity output.
    '''
    pass
    '''
    # Generate adjusted industry output by location
    IndustryOutput <- model$MultiYearIndustryOutput[, as.character(year)]
    # Use CommodityMix to transform IndustryOutput to CommodityOutput
    CommodityMix <- generateCommodityMixMatrix(model)
    CommodityOutput <- as.numeric(CommodityMix %*% IndustryOutput)
    return(CommodityOutput)
    '''

#TODO
def transform_industry_cpi_to_commodity_cpi_for_year(year, model):
    '''
    #' Generate Commodity CPI by transforming Industry CPI using Commodity Mix matrix.
    #' @param year Year of Industry CPI.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @return A dataframe contains adjusted Commodity CPI.
    '''
    # Generate adjusted industry CPI by location
    IndustryCPI = model.MultiYearIndustryCPI[[f"{year}"]]
    # Use MarketShares (of model IO year) to transform IndustryCPI to CommodityCPI
    MarketShares = generate_market_shares_from_make(model)
    # The transformation is essentially a I x 1 matrix %*% a C x I matrix which yields a C x 1 matrix
    CommodityCPI = np.matmul(IndustryCPI, MarketShares) # CommodityCPI <- as.numeric(IndustryCPI %*% MarketShares)
    # Non-industry sectors would have CommodityCPI of 0
    # To avoid interruption in later calculations, they are forced to 100
    CommodityCPI[CommodityCPI == 0] = 100
    # Validation: check if IO year CommodityCPI is 100
    if (year == 2012):
        err = utility_functions.unlist(abs(100-CommodityCPI) > 0.3)
        if sum(err) > 0:
            msg = "Error in CommodityCPI"
            logging.error(msg)
            sys.exit(msg)
    return(CommodityCPI)


#TODO
def transform_direct_requirements_with_market_shares(B, D, model):
    '''
    #' Transform Direct Requirements matrix with Market Shares matrix, works for both commodity-by-commodity and industry-by-industry model types.
    #' @param B Marginal impact per unit of the environmental flows.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param D Market Shares matrix.
    #' @return Direct Requirements matrix.
    '''
    pass
    '''
    # Only generate result if the column names of the direct requirements table match the row names of the market shares matrix
    if (all(colnames(B) == rownames(D)) && all(colnames(D) == rownames(B))) {

    } else {
        stop("Column names of the direct requirements do not match the row names of the market shares matrix.")
    }
    if (model$specs$CommodityorIndustryType == "Commodity") {
        # commodity model DR_coeffs = dr %*% ms (CxI x IxC) = CxC
        A <- B %*% D
        dimnames(A) <- c(dimnames(B)[1], dimnames(D)[2])
    } else if (model$specs$CommodityorIndustryType == "Industry") {
        # industry model DR_coeffs = ms %*% dr (IxC x CxI) = IxI
        A <- D %*% B
        dimnames(A) <- c(dimnames(D)[1], dimnames(B)[2])
    } else {
        stop("CommodityorIndustryType not specified or incorrectly specified for model.")
    }
    return(A)
    '''

#TODO: test implementation
def transform_final_demand_with_market_shares(fdf, model): 
    '''
    Transform Final Demand (commodity x sector) with Market Shares matrix
    to Final Demand (industry x sector)

    Arguments:
    Fdf:    Final Demand dataFrame.
    model:  A complete EEIO model: a list with USEEIO model components and attributes.

    return: Final Demand (industry x sector) dataFrame
    '''
    D = generate_market_shares_from_make(model)
    # See Miller and Blair section 5.3.7 (pg 197)
    Fmatrix = np.matmul(D, fdf)
    return(pd.DataFrame(Fmatrix))

#TODO
def calculate_leontif_inverse(A):
    '''
    #' Calculate Leontief inverse from direct requirements matrix.
    #' @param A Direct Requirements matrix.
    #' @return Leontief inverse.
    '''
    pass
    '''
    I <- diag(nrow(A))
    L <- solve(I-A)
    return(L)
    '''

#DONE
def generate_domestic_use(use, model): 
    '''
    Generate domestic Use table by adjusting Use table based on Import matrix.

    Arguments:
    Use:    dataframe of a Use table
    model:  An EEIO model object with model specs and crosswalk table loaded
    
    return: A Domestic Use table with rows as commodity codes and 
            columns as industry and final demand codes
    '''
    # Load Import matrix
    if model.specs["BaseIOLevel"] != "Sector":
        imp = pd.read_parquet(importlib.resources.files('useeio_py.data2').joinpath(
            f"{model.specs['BaseIOLevel']}_Import_{model.specs['IOYear']}_BeforeRedef.parquet"
        )).set_index('index').select_dtypes(include=['number']) * 1E6
        
    else:
        imp = pd.read_parquet(importlib.resources.files('useeio_py.data2').joinpath(
            f"Summary_Import_{model.specs['IOYear']}_BeforeRedef.parquet"
        )).set_index('index').select_dtypes(include=['number']) * 1E6

        imp = pd.DataFrame(utility_functions.aggregate_matrix(imp, "Summary", "Sector", model))
    
    # subtract import from use
    domestic_use = use - imp.loc[list(use.index)][list(use.columns)]
    
    # adjust import column in domestic_use to 0
    # Note: the original values in Import column are essentially the International Trade Adjustment
    #       that are reserved and added as an additional column (F050/F05000) in DomesticUse.
    cols = utility_functions.get_vector_of_codes(
        model.specs['BaseIOSchema'],
        model.specs['BaseIOLevel'],
        "Import"
        )['Code']
    domestic_use[cols] = 0
    return(domestic_use)

#DONE
def generate_international_trade_adjustment_vector(use, model):
    '''
    Generate international trade adjustment vector from Use and Import matrix.
    
    Arguments:
    Use:    dataframe of a Use table
    model:  An EEIO model object with model specs and crosswalk table loaded

    return: An international trade adjustment vector with commodity codes as index
    '''
    # Load Import matrix
    if model.specs["BaseIOLevel"] != "Sector":
        imp = pd.read_parquet(importlib.resources.files('useeio_py.data2').joinpath(
            f"{model.specs['BaseIOLevel']}_Import_{model.specs['IOYear']}_BeforeRedef.parquet"
        )).set_index('index').select_dtypes(include=['number']) * 1E6
        
    else:
        imp = pd.read_parquet(importlib.resources.files('useeio_py.data2').joinpath(
            f"Summary_Import_{model.specs['IOYear']}_BeforeRedef.parquet"
        )).set_index('index').select_dtypes(include=['number']) * 1E6

        imp = pd.DataFrame(utility_functions.aggregate_matrix(imp, "Summary", "Sector", model))
    # Define Import code
    import_code = utility_functions.get_vector_of_codes(
        model.specs['BaseIOSchema'],
        model.specs['BaseIOLevel'],
        'Import'
    )['Code']
    # Calculate InternationalTradeAdjustment
    # In the Import matrix, the imports column is in domestic (US) port value.
    # But in the Use table, it is in foreign port value.
    # domestic port value = foreign port value + value of all transportation and insurance services to import + customs duties
    # See documentation of the Import matrix (https://apps.bea.gov/industry/xls/io-annual/ImportMatrices_Before_Redefinitions_DET_2007_2012.xlsx)
    # So, InternationalTradeAdjustment = Use$Imports - Import$Imports
    # InternationalTradeAdjustment is essentially 'value of all transportation and insurance services to import' and 'customs duties'
    
    intl_trade_adj = use[import_code] - imp.loc[list(use.index)][import_code]
    return(intl_trade_adj)
