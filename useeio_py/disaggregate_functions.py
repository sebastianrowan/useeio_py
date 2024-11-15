# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from . import configuration_functions, load_io_tables
from .utility_functions import get_index
import logging
import importlib
import yaml
import os
import sys

#TODO: Update all function documentation


def disaggregate_model(model):
    '''
    #' Disaggregate a model based on specified source file
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return A disaggregated model.
    '''
    logging.info("Initializing Disaggregation of IO tables...")

    for key in model.DisaggregationSpecs:
        disagg = model.DisaggregationSpecs[key]
        # Disaggregating sector lists 
        logging.debug("calling func...")
        model.Commodities = disaggregate_sector_dfs(model, disagg, "Commodity")
        logging.debug("calling func...")
        model.Industries = disaggregate_sector_dfs(model, disagg, "Industry")

        # Disaggregating main model components
        logging.debug("calling func...")
        model.UseTransactions = disaggregate_use_table(model, disagg)
        logging.debug("calling func...")
        model.MakeTransactions = disaggregate_make_table(model, disagg)
        logging.debug("calling func...")
        model.UseValueAdded = disaggregate_va(model, disagg)
        logging.debug("calling func...")
        model.DomesticUseTransactions = disaggregate_use_table(model, disagg, domestic=True)

        if model.specs['CommodityorIndustryType'] == "Commodity":
            logging.debug("calling func...")
            model.FinalDemand = disaggregate_final_demand(model, disagg, domestic=False)
            logging.debug("calling func...")
            model.DomesticFinalDemand = disaggregate_final_demand(model, disagg, domestic=True)
        else:
            logging.debug("calling func...")
            model.FinalDemandbyCommodity = disaggregate_final_demand(model, disagg, domestic=False)
            logging.debug("calling func...")
            model.DomesticFinalDemandbyCommodity = disaggregate_final_demand(model, disagg, domestic=True)
            logging.debug("calling func...")
            model.InternationalTradeAdjustmentbyCommodity = disaggregate_international_trade_adjustment(
                model, disagg, None, adjustmentByCommodity = True
            )
        
        # Balancing model
        if disagg['DisaggregationType'] == "Userdefined":
            logging.debug("calling func...")
            model = balance_disagg(model, disagg)

        # Recalculate model$CommodityOutput and model$IndustryOutput objects.
        # This if else has to be separate from the one above because 
        # the calculateIndustryCommodityOutput function is used prior to the creation
        # of model$FinalDemandbyCommodity object, and we can't recalculate the
        # commodity and industry totals before balancing.
        if model.specs['CommodityorIndustryType'] == "Commodity":
            logging.debug("calling func...")
            model = load_io_tables.calculate_industry_commodity_output(model)
        else:
            logging.debug("calling func...")
            model.IndustryOutput = np.sum(model.UseTransactions, axis=0) + np.sum(model.UseValueAdded, axis=0)
            logging.debug("calling func...")
            model.CommodityOutput = np.sum(model.UseTransactions, axis=1) + np.sum(model.UseValueAdded, axis=1)

        # Disaggregating MultiyearIndustryOutput and MultiYearCommodityOutput 
        logging.debug("calling func...")
        model.MultiYearCommodityOutput = disaggregate_multi_year_output(model, disagg, output_type = "Commodity")
        logging.debug("calling func...")
        model.MultiYearIndustryOutput = disaggregate_multi_year_output(model, disagg, output_type = "Industry")



def get_disaggregation_specs(model, config_paths = None):
    '''
    #' Obtain aggregation and disaggregation specs from input files
#' @param model An EEIO model object with model specs and IO tables loaded
#' @param configpaths str vector, paths (including file name) of disagg configuration file(s).
#' If NULL, built-in config files are used.
#' @return None
    '''
    logging.debug("check")
    model.DisaggregationSpecs = dict()
    for configFile in model.specs['DisaggregationSpecs']:
        logging.info(f"Loading disaggregation specification file for {configFile}...")
        logging.debug("calling func...")
        config = configuration_functions.get_configuration(configFile, "disagg", config_paths)

        if('Disaggregation' in config.keys()):
            for key in config['Disaggregation']:
                model.DisaggregationSpecs[key] = config['Disaggregation'][key]

    model = disaggregate_setup(model, config_paths)
    return(model)

#TODO: Test implementation
def disaggregate_setup(model, config_paths = None):
    '''
    #' Setup the configuration specs based on the input files
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @param configpaths str vector, paths (including file name) of disagg configuration file(s).
    #' If NULL, built-in config files are used.
    #' @return A model object with the correct disaggregation specs.
    '''
    for key in model.DisaggregationSpecs:
        disagg = model.DisaggregationSpecs[key]
        fname = f"inst/extdata/disaggspecs/{disagg['SectorFile']}" if config_paths is None \
            else f"{os.path.dirname(config_paths)}/{disagg['SectorFile']}"
        filename = importlib.resources.files('useeio_py').joinpath(fname)
        disagg['NAICSSectorCW'] = pd.read_csv(
            # try using importlib.resources.files() 
            filename,
            delimiter = ","
        )
        newNames = pd.DataFrame({
            "SectorCode": disagg['NAICSSectorCW']['USEEIO_Code'],
            "SectorName": disagg['NAICSSectorCW']['USEEIO_Name'],
            "Category": disagg['NAICSSectorCW']['Category'],
            "Subcategory": disagg['NAICSSectorCW']['Subcategory'],
            "Description": disagg['NAICSSectorCW']['Description']
        }).drop_duplicates()

        disagg['DisaggregatedSectorNames'] = newNames['SectorName'].astype('string')
        disagg['DisaggregatedSectorCodes'] = newNames['SectorCode'].astype('string')
        disagg['Category'] = newNames['Category'].astype('string')
        disagg['Subcategory'] = newNames['Subcategory'].astype('string')
        disagg['Description'] = newNames['Description'].astype('string')

        ''' This R code seems redundent to me. #TODO: Check implementation
        # My impression of this code is that is takes a list, reduces it to unique values
        #  and then recreates the original list from the unique values

        disagg$DisaggregatedSectorNames <- as.list(levels(newNames[, 'SectorName']))
        disagg$DisaggregatedSectorCodes <- as.list(levels(newNames[, 'SectorCode']))
        disagg$Category <- lapply(newNames[, 'Category'], as.character)
        disagg$Subcategory <- lapply(newNames[, 'Subcategory'], as.character)
        disagg$Description <- lapply(newNames[, 'Description'], as.character)
        
        #reordering disaggSectorNames and DisaggSectorCodes to match the mapping in newNames
        disagg$DisaggregatedSectorNames <- as.list(disagg$DisaggregatedSectorNames[match(newNames$SectorName,disagg$DisaggregatedSectorNames)])
        disagg$DisaggregatedSectorCodes <- as.list(disagg$DisaggregatedSectorCodes[match(newNames$SectorCode,disagg$DisaggregatedSectorCodes)])
        '''

        # Load Make table disaggregation file
        if disagg['MakeFile'] is not None:
            fname = f"inst/extdata/disaggspecs/{disagg['MakeFile']}" if config_paths is None \
            else f"{os.path.dirname(config_paths)}/{disagg['MakeFile']}"
            
            filename = importlib.resources.files('useeio_py').joinpath(fname)
            disagg['MakeFileDF'] = pd.read_csv( #TODO: probably will have to use importlib.resources.files()
                filename,
                delimiter = ","
            )

        # Load Use table disaggregation file
        if disagg['UseFile'] is not None:
            fname = f"inst/extdata/disaggspecs/{disagg['UseFile']}" if config_paths is None \
            else f"{os.path.dirname(config_paths)}/{disagg['UseFile']}"
            
            filename = importlib.resources.files('useeio_py').joinpath(fname)

            disagg['UseFileDF'] = pd.read_csv( #TODO: probably will have to use importlib.resources.files()
                filename,
                delimiter = ","
            )

        # Load Environment flows table
        if disagg['EnvFile'] is not None:
            f = f"inst/extdata/disaggspecs/{disagg['EnvFile']}" if config_paths is None \
            else f"{os.path.dirname(config_paths)}/{disagg['EnvFile']}"
            
            filename = importlib.resources.files('useeio_py').joinpath(fname)
            disagg['EnvFileDF'] = pd.read_csv( #TODO: probably will have to use importlib.resources.files()
                filename,
                delimiter = ","
            )

        disagg['EnvAlloc'] = True if "FlowRatio" in disagg['EnvFileDF'].columns else False

        # For Two-region model, develop two-region specs from national disaggregation files
        if model.specs['IODataSource'] == 'stateior' and disagg['OriginalSectorCode'][-3:] == "/US":
            for region in model.specs['ModelRegionAcronyms']:
                d2 = prepare_two_region_disaggregation(disagg, region, model.specs['ModelRegionAcronyms'])
                model.DisaggregationSpecs[d2['OriginalSectorCode']] = d2
            # Remove original disaggregation spec
            model.DisagregationSpecs[disagg['OriginalSectorCode']] = None
        else:
            model.DisaggregationSpecs[disagg['OriginalSectorCode']] = disagg
            
        return(model)


def prepare_two_region_disaggregation(disagg, region, regions):
    '''
    #' Generate two-region disaggregation specs from a national spec
#' @param disagg Specifications for disaggregating the current Table
#' @param region Str, Location code for target disaggregation specs
#' @param regions list of location codes from ModelRegionAcronyms
#' @return modified disagg specs for target region
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_international_trade_adjustment(model, disagg, ratios = None, adjustmentByCommodity = False):
    '''
    #' Disaggregate model$InternationalTradeAdjustments vector in the main model object
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param ratios Specific ratios to be used for the disaggregation of the InternationalTradeAdjusment object in place of using economic totals to derive the ratios.
#' @param adjustmentByCommodity Flag to denote whether to disaggregate the InternationalTradeAdjustmentbyCommodity object which is only present in industry models
#' @return newInternationalTradeAdjustment A vector which contains the InternationalTradeAdjustment for the disaggregated sectors
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_margins(model, disagg):
    '''
    #' Disaggregate model$Margins dataframe in the main model object
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return newMargins A dataframe which contain the margins for the disaggregated sectors
    '''
    logging.debug("Function not implemented")
    sys.exit()

#TODO: check implementation
def disaggregate_multi_year_output(model: "USEEIOModel", disagg: dict, output_type: str = "Commodity"):
   #' Disaggregate MultiYear Output model objects
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param disagg Specifications for disaggregating the current Table
    #' @param output_type A string that indicates whether the Commodity or Industry output should be disaggregated
    #' @return model A dataframe with the disaggregated GDPGrossOutputIO by year 
    if output_type == "Industry":
        originalOutput = model.MultiYearIndustryOutput
    else:
        #assume commodity if industry is not specified
        originalOutput = model.MultiYearCommodityOutput
    
    logging.debug("calling func...")
    disaggRatios = disaggregated_ratios(model, disagg, output_type)
    # Obtain row with original vector in GDPGrossOutput object
    #TODO: I don't understand what this code is supposed to do exactly. Will have to write tests for the actual code to see behavior
    #   OriginalVectorIndex is the location in the DataFrame of the sector to be disaggregated
    #   r code uses which(rownames(...)). Because rownames must be unique, this will always return the first instance
    #   subsequent rows for the same sector would have .1, .2, etc. appended to name. 
    originalVectorIndex = originalOutput[originalOutput.index == disagg["OriginalSectorCode"]].index[0]
    print(originalVectorIndex)
    print("DEBUG")
    sys.exit()
    
    originalVector = originalOutput[originalOutput.index == disagg['OriginalSectorCode']]
    # Create new rows where disaggregated values will be stored
    disaggOutput = pd.DataFrame(
        np.tile(originalVector.values, reps=(len(disagg['DisaggregatedSectorCodes']), 1)),
        columns = originalVector.columns
    )

    # apply ratios to values
    disaggOutput = disaggOutput * disaggRatios.T()
    
    # rename rows
    disaggOutput.index = disagg['DisaggregatedSectorCodes']

    # bind new values to original table
    #TODO: check this: I believe code should be inserting disaggOutput at the specifiec index location,
    #  replacing the single row to be disaggregated
    newOutputTotals = pd.concat([originalVector, disaggOutput, originalOutput])

    logging.debug("Function docstring says this function should return value. Currently returning None...")
    ''' R code for comparison because I am not sure about the translation of this part
    #bind new values to original table
    newOutputTotals <- rbind(originalOutput[1:originalVectorIndex-1,], disaggOutput, originalOutput[-(1:originalVectorIndex),])
    '''

def disaggregated_ratios(model, disagg, output_type = "Commodity"):
    '''
    #' Calculate ratios of throughputs from the disaggregated sectors
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param output_type A string value indicating whether to obtain "Commodity" or "Industry" ratios
#' @return disaggRatios A dataframe which contain the disaggregated ratios for the disaggregated sectors
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_sector_dfs(model: "USEEIOModel", disagg: dict, list_type: str = "Industry"):
    '''
    Disaggregate model.Commodity or model.Industry dataframes in the main model object.

    Parameters
    ----------
    model : USEEIOModel
        An EEIO model object with model specs and IO tables loaded.
    disagg : dict
        Specifications for disaggregating the current table
    list_type : str
        A string indicating whether to disaggregate model.Industry or model.Commodity

    Returns
    -------
    new_sectors : DataFrame
        A DataFrame which contains the disaggregated model.Commodity or model.Industry table
    '''
    logging.debug("check")
    
    if list_type == "Commodity":
        original_list = model.Commodities.copy(deep=True)
    else:
        original_list = model.Industries.copy(deep=True)

    original_index = get_index(original_list["Code_Loc"], disagg["OriginalSectorCode"])
    
    new_sectors = pd.DataFrame(np.empty([disagg["DisaggregatedSectorCodes"].shape[0], original_list.shape[1]]))
    new_sectors.columns = original_list.columns.copy()
    if list_type == "Commodity":
        new_sectors['Category'] = disagg['Category']
        new_sectors['Subcategory'] = disagg['Subcategory']
        new_sectors['Description'] = disagg['Description']

    new_sectors["Code"] = disagg['DisaggregatedSectorCodes'].iloc[0].split("/")[0]
    new_sectors["Code_Loc"] = disagg['DisaggregatedSectorCodes']
    new_sectors["Name"] = disagg['DisaggregatedSectorNames']

    # insert new_sectors into original_list at location of original_index
    new_sectors = pd.concat([original_list.iloc[:original_index-1], new_sectors, original_list.iloc[original_index:]])
    return(new_sectors)

def disaggregate_satellite_subset_by_ratio(sat_table, disagg, allocating_sectors, allocation_vector = None):
    '''
    #' Disaggregate a portion of a satellite table based on an allocation_vector
#' @param sattable A standardized satellite table to be disaggregated.
#' @param disagg Specifications for disaggregating the current Table
#' @param allocating_sectors vector of sectors to allocate to
#' @param allocation_vector named vector of allocation ratios
#' @return A satellite table with new sectors added.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_satellite_table(disagg, tbs, sat_spec):
    '''
    #' Disaggregate satellite tables from static file based on specs
#' @param disagg Specifications for disaggregating the current Table
#' @param tbs A standardized satellite table with resource and emission names from original sources.
#' @param sat_spec, a standard specification for a single satellite table.
#' @return A standardized satellite table with old sectors removed and new sectors added.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_make_table(model: "USEEIOModel", disagg: dict):
    '''
    #' Disaggregate make table based on specs
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return A standardized make table with old sectors removed and new sectors added.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_use_table(model: "USEEIOModel", disagg: dict, domestic: bool = False):
    '''
    Disaggregate Use table based on specs

    Parameters
    ----------
    model : USEEIOModel
        A complete EEIO model
    disagg : dict
        Specifications for disaggregating the current table
    domestic : bool
        A logical value indicating whether to disaggregate final demand.

    Returns
    -------
    disagg_table : DataFrame
        An disaggregated UseTable.
    '''
    logging.debug("check")
    # specify the type of disaggregation
    disaggType = disagg['DisaggregationType']

    #disaggregation can be of types "Predefined" or "UserDefined".
    if (disaggType == "Predefined" or disagg['UseFileDF'] is None):
        table = model.DomesticUseTransactions if domestic else model.UseTransactions
        logging.debug("calling func...")
        disaggTable = uniform_disagg(model, disagg, table)
    elif (disaggType == "Userdefined"):
        logging.debug("calling func...")
        disaggTable = specified_use_disagg(model, disagg, domestic)
    else:
        logging.error("Disaggregation not performed, type not defined")
        sys.exit()
    '''
  #specify type of disaggregation
  disaggType = disagg$DisaggregationType
  
  #disaggregation can be of types "Predefined" or "UserDefined". 
  if(disaggType == "Predefined" | is.null(disagg$UseFileDF)) {
    if(domestic) {
      table <- model$DomesticUseTransactions
    } else {
      table <- model$UseTransactions
    }
    disaggTable <- uniformDisagg(model, disagg, table)
  } else if(disaggType == "Userdefined") {
    disaggTable <- specifiedUseDisagg(model, disagg, domestic)
  } else {
    stop("Disaggregation not performed, type not defined")
  }

  return(disaggTable)
    '''
    logging.debug("Function not implemented")
    sys.exit()


def disaggregate_final_demand(model: "USEEIOModel", disagg: dict, domestic: bool = False):
    '''
    #' Disaggregate Final Demand based on specs
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param domestic A logical value indicating whether to disaggregate domestic final demand.
#' @return A standardized final demand table with old sectors removed and new sectors with manual and default allocations added.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_va(model: "USEEIOModel", disagg: dict):
    '''
    #' Disaggregate Value Added based on specs
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return A standardized Vale Added table with old sectors removed and new sectors with manual and default allocations added.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def uniform_disagg(model: "USEEIOModel", disagg: dict, table: "DataFrame"):
    '''
    Disaggregate make or use table uniformly based on the number of new sectors

    Parameters
    ----------
    model : USEEIOModel
        A complete EEIO model
    disagg : dict
        Specifications for disaggregating the current Table
    table : DataFrame 
        make or use table

    Returns
    -------
    DataFrame
        A standardized make table with old sectors removed and new, uniformly disaggregated sectors added.
    '''
    logging.debug("check")
    # Predefined disaggregation assumes 1 industry/commodity disaggregated uniformly into several, with  
    #  values along the intersections disaggregated uniformly along the diagonal.

    #Determine number of commodities and industries in DisaggSpecs
    print(disagg['DisaggregatedSectorCodes'].shape)
    '''
    #Predefined disaggregation assumes 1 industry/commodity disaggregated uniformly into several, with  
  #values along the intersections disaggregated uniformly along the diagonal.

  #Determine number of commodities and industries in DisaggSpecs
  numNewSectors <- length(disagg$DisaggregatedSectorCodes) 
  
  #Determine commodity and industry indeces corresponding to the original sector code
  originalRowIndex <- which(rownames(table)==disagg$OriginalSectorCode)
  originalColIndex <- which(colnames(table)==disagg$OriginalSectorCode)

  ########Row disaggregation
  #Copy original row (ind) for disaggregation
  originalRowVector <- table[originalRowIndex,]
  
  disaggRows <- disaggregateRow(originalRowVector,disagg)
  
  ########Column disaggregation
  #Copy original Column (Com) for disaggregation
  originalColVector <-table[,originalColIndex, drop = FALSE]#drop = False needed to copy as dataframe
  
  disaggCols <- disaggregateCol(originalColVector,disagg)
  
  
  ########Intersection Disaggregation
  originalIntersection <- table[originalRowIndex, originalColIndex]
  
  #Divide intersection by number of new sectors
  originalIntersection <- originalIntersection/numNewSectors
  
  #Populate disaggregated intersection assuming equal values along the diagonal. Matrix variable. 
  disaggIntersection <- diag(originalIntersection,numNewSectors,numNewSectors)
  
  #Convert to data frame
  disaggIntersection = as.data.frame(t(disaggIntersection))
  
  #rename rows and columns
  colnames(disaggIntersection) <- disagg$DisaggregatedSectorCodes
  rownames(disaggIntersection) <- disagg$DisaggregatedSectorCodes
  
  
  disaggTable <- assembleTable(table, disagg, disaggCols, disaggRows, disaggIntersection)
  
  return(disaggTable)
    '''

    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_rows(row_vectors, disagg_specs, duplicate=False, not_uniform = False):
    '''
    #' Disaggregate multiple rows from a table.
#' @param RowVectors A dataframe containing the rows to disaggregate
#' @param disagg_specs Specifications for disaggregating the current Table
#' @param duplicate A flag that indicates whether the disaggregated rows are to be duplicated or not (e.g. for CPI values)
#' @param notUniform A flag that indicates whether the disaggregated rows are to be disaggregated in uniform manner or not
#' @return A dataframe with disaggregated rows.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_cols(col_vectors, disagg_specs, duplicate=False, not_uniform = False):
    '''
    #' Disaggregate multiple columns from a table.
#' @param ColVectors A dataframe containing the columns to disaggregate
#' @param disagg_specs Specifications for disaggregating the current Table
#' @param duplicate A flag that indicates whether the disaggregated columns are to be duplicated or not (e.g. for CPI values)
#' @param notUniform A flag that indicates whether the disaggregated columns are to be disaggregated in uniform manner or not
#' @return A dataframe with disaggregated columns.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_row(original_row_vector, disagg_specs, duplicate=False, not_uniform = False):
    '''
    #' Disaggregate a single row from a table.
#' @param originalRowVector A dataframe containing the row to disaggregate
#' @param disagg_specs Specifications for disaggregating the current Table
#' @param duplicate A flag that indicates whether the disaggregated row is to be duplicated or not (e.g. for CPI values)
#' @param notUniform A flag that indicates whether the disaggregated row is to be disaggregated in uniform manner or not
#' @return A dataframe with the original row disaggregated.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_col(original_col_vector, disagg_specs, duplicate=False, not_uniform = False):
    '''
    #' Disaggregate a single column from a table.
#' @param originalColVector A dataframe containing the column to disaggregate
#' @param disagg_specs Specifications for disaggregating the current Table
#' @param duplicate A flag that indicates whether the disaggregated columns are to be duplicated or not (e.g. for CPI values)
#' @param notUniform A flag that indicates whether the disaggregated columns are to be disaggregated in uniform manner or not
#' @return A dataframe with the original column disaggregated.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def disaggregate_master_crosswalk(model: "USEEIOModel", disagg: dict):
    '''
    #' Disaggregate the MasterCrosswalk to include the new sectors for disaggregation
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return crosswalk with new sectors added.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def specified_make_disagg(model: "USEEIOModel", disagg: dict):
    '''
    #' Disaggregate make table based on the allocations specified in the files referenced in the diaggregation specs.
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return A standardized make table with old sectors removed and new disaggregated sectors added based on the allocations in the disaggregation specs.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def specified_use_disagg(model: "USEEIOModel", disagg: dict, domestic = False):
    '''
    Disaggregate use table based on the allocations specified in the files referenced in the disaggregation specs.

    Parameters
    ----------
    model : USEEIOModel
        A complete EEIO model: a list with USEEIO model components and attributes.
    disagg : dict
        Specifications for disaggregating the current Table
    domestic : bool
        Flag that indicates where to use the Domestic Use or UseTransactions table
    
    Returns
    -------
    DataFrame
        A standardized make table with old sectors removed and new disaggregated sectors added based on the allocations in the disaggregation specs.
    '''
    logging.debug("check")
    # Local variable for original sector code
    originalSectorCode = disagg["OriginalSectorCode"]
    # Local variable for new sector codes
    newSectorCodes = disagg["DisaggregatedSectorCodes"]
    # Local variable for Use table allocations
    UseAllocations = disagg["UseFileDF"]
    # Column names in Final Demand
    fdColNames = model.FinalDemand.columns
    VARowNames = model.UseValueAdded.index

    if domestic:
        originalUse = model.DomesticUseTransactions
    else:
        originalUse = model.UseTransactions

    ### Disaggregate Use Rows, Columns, and Intersection while using the ###
    #   allocation data extracted from the Disaggregation.csv              #

    # Extracting intersection allocation. Get rows of DF where only new sector codes are present in both the industryCode and commodityCode columns. 

    
    intersectionPercentages = UseAllocations.loc[
        (UseAllocations["IndustryCode"].isin(newSectorCodes)) &
        (UseAllocations["CommodityCode"].isin(newSectorCodes))
    ]

    # Applying allocations for disaggregated intersection
    logging.debug("calling func...")
    disaggregatedIntersection = apply_allocation(disagg, intersectionPercentages, "UseIntersection", originalUse)


    '''
    intersectionPercentages <-subset(UseAllocations, IndustryCode %in% newSectorCodes & CommodityCode %in% newSectorCodes)
    
    #Applying allocations for disaggregated intersection
    disaggregatedIntersection <- applyAllocation(disagg,intersectionPercentages,"UseIntersection", originalUse)

    #Allocations for column (industry) disaggregation. 
    #Get rows of the DF which do not contain the original sector code or the new sector codes in the commodity column,
    #where no VA row names are present in the commodity Column, and only the new sector codes are present in the industry column
    colPercentages <- subset(UseAllocations, !(CommodityCode %in% originalSectorCode) & !(CommodityCode %in% newSectorCodes) & !(CommodityCode %in% VARowNames) & IndustryCode %in% newSectorCodes)
    
    #Applying allocation to disaggregat columns
    disaggregatedColumns <- applyAllocation(disagg,colPercentages,"UseCol", originalUse) 

    #Allocations for the row (commodity) disaggregation. Get all rows of the DF where:
    #new sector codes are in the CommodityCode column; the FD column codes are not in the IndustryCode; 
    #and neither the original nor new sector codes are in the IndustryCode column. 
    rowsPercentages <- subset(UseAllocations, CommodityCode %in% newSectorCodes & !(IndustryCode %in% fdColNames) & !(IndustryCode %in% originalSectorCode) & !(IndustryCode %in% newSectorCodes))

    #Assigning allocations for disaggregated rows
    disaggregatedRows  <- applyAllocation(disagg,rowsPercentages,"UseRow", originalUse)

    DisaggUse <- assembleTable(originalUse, disagg, disaggregatedColumns, disaggregatedRows, disaggregatedIntersection)

    return(DisaggUse)
    '''
    logging.debug("Function under construction...")
    sys.exit()

def assemble_table(original_table, disagg, disagg_cols, disagg_rows, disagg_intersection):
    '''
    #' Assemble Table from the various disaggregated components.
#' @param originalTable Dataframe. The original table before disaggregation
#' @param disagg Specifications for disaggregating the current Table
#' @param disaggCols Dataframe. Previously disaggregated columns of the table.
#' @param disaggRows Dataframe. Previously disaggregated rows of the table.
#' @param disaggIntersection Dataframe. Previously disaggregated intersection of the table.
#' @return The Disaggregated table as a dataframe with the disaggregated rows, columns, and intersection included
    '''
    logging.debug("Function not implemented")
    sys.exit()

def apply_allocation(disagg: dict, alloc_percentages: "DataFrame", vector_to_disagg: str, original_table: "DataFrame"):
    '''
    Allocate values specified by the .yml disaggregation specs to the correct
    places in a disaggregated row/column of the Use/Make tables. 

    Parameters
    ----------
    disagg : dict
        Specifications for disaggregating the current Table
    alloc_percentages : Dataframe
        A subset of the dataframe that contains the percentages to allocate to specific industry and commodity combinations in the disaggregated vector. Parameter use coordinated with @param vectorToDisagg
    vector_to_disagg : str
        A parameter to indicate what table and what part of that table is being disaggregated
        (e.g. "MakeCol" or "Intersection") 
    originalTable : Dataframe. The original dataframe upon which allocation is performed (e.g., Make or Use)

    Returns
    -------
    DataFrame
        A dataframe with the values specified in the disaggSpecs assigned to the correct Make or Use table indeces.
    '''
    logging.debug("check")

    # Local variable for new sector codes
    newSectorCodes = disagg["DisaggregatedSectorCodes"]
    numNewSectors = newSectorCodes.shape[0]
    # Local variable for original sector code
    originalSectorCode = disagg["OriginalSectorCode"]

    # These different if blocks are needed because of the difference dimensions
    #  of the manual and default allocation vectors needed for disaggregating
    #  the Make and Use rows and columns. Each block initializes the manual and
    #  default allocation values for the relevant rows or columns.

    if(vector_to_disagg == "MakeRow"): 
        # Set up for manual allocations
        # Get commodity and/or industry indices corresponding to the original
        #  sector code
        # Get original row or column
        originalVector = original_table.loc[originalSectorCode] #TODO: check this
        logging.debug(f"Code not implemented for vector_to_disagg == {vector_to_disagg}")
        sys.exit()
        '''
        #Create new rows to store manual allocation values (all other values initiated to NA)
        manualAllocVector <- data.frame(matrix(ncol = ncol(originalTable), nrow = length(newSectorCodes)))
        
        #Assign correct column and row names to new rows dataframe
        colnames(manualAllocVector) <- names(originalVector)
        rownames(manualAllocVector) <- newSectorCodes
        
        #Assign lookup index for allocPercentages vector 
        allocPercentagesRowIndex <- 1
        allocPercentagesColIndex <- 2

        defaultPercentages <- getDefaultAllocationPercentages(disagg$MakeFileDF, disagg,
                                                            numNewSectors, output='Commodity')

        #Create new rows to store default allocation values by copying the original row a number of times equal to the number of new sectors
        defaultAllocVector <- rbind(originalVector, originalVector[rep(1,numNewSectors-1),])
        #multiply all elements in row by default percentages to obtain default allocation values
        defaultAllocVector <- defaultAllocVector*defaultPercentages[,1]
        
        #Assign correct column and row names to new rows dataframe
        colnames(defaultAllocVector) <- names(originalVector)
        rownames(defaultAllocVector) <- newSectorCodes
        '''
    elif (vector_to_disagg == "MakeCol"):
        logging.debug(f"Code not implemented for vector_to_disagg == {vector_to_disagg}")
        sys.exit()
        '''
        #Get commodity and/or industry indeces corresponding to the original sector code
        originalVectorIndex <- which(colnames(originalTable)==disagg$OriginalSectorCode)
        #Get original row or column
        originalVector <- originalTable[,originalVectorIndex, drop = FALSE]

        #Create new cols to store allocation values (all other values initiated to NA)
        manualAllocVector <- data.frame(matrix(ncol = length(newSectorCodes), nrow = nrow(originalTable)))
        
        #Assign correct column and row names to new rows dataframe
        colnames(manualAllocVector) <- newSectorCodes
        rownames(manualAllocVector) <- rownames(originalVector)
        
        #Assign lookup index for allocPercentages vector 
        allocPercentagesRowIndex <- 1
        allocPercentagesColIndex <- 2
        
        defaultPercentages <- getDefaultAllocationPercentages(disagg$MakeFileDF, disagg,
                                                            numNewSectors, output='Commodity')
        
        #Create new columns to store default allocation values by copying the original column a number of times equal to the number of new sectors
        defaultAllocVector <- cbind(originalVector, originalVector[,rep(1,numNewSectors-1)])
        #multiply all elements in row by default percentages to obtain default allocation values
        defaultAllocVector <- data.frame(t(t(defaultAllocVector)*defaultPercentages[,1]))
        
        #Assign correct column and row names to new rows dataframe
        colnames(defaultAllocVector) <- newSectorCodes
        rownames(defaultAllocVector) <- rownames(originalVector)
        '''
    elif (vector_to_disagg == "MakeIntersection"):
        logging.debug(f"Code not implemented for vector_to_disagg == {vector_to_disagg}")
        sys.exit()

        '''
        intersection <- originalTable[which(rownames(originalTable)==disagg$OriginalSectorCode),
                                  which(colnames(originalTable)==disagg$OriginalSectorCode), drop=FALSE]

        defaultPercentages <- getDefaultAllocationPercentages(disagg$MakeFileDF, disagg,
                                                            numNewSectors, output='Commodity')
        
        defaultAllocVector <- calculateDefaultIntersection(intersection, defaultPercentages, newSectorCodes)

        manualAllocVector <- createBlankIntersection(newSectorCodes)
        
        #Assign lookup index for allocPercentages vector 
        allocPercentagesRowIndex <- 1
        allocPercentagesColIndex <- 2
        '''
    elif (vector_to_disagg in ["UseRow", "FinalDemand"]):
        logging.debug(f"Code not implemented for vector_to_disagg == {vector_to_disagg}")
        sys.exit()

        '''
        #Get commodity and/or industry indeces corresponding to the original sector code
        originalVectorIndex <- which(rownames(originalTable)==disagg$OriginalSectorCode)
        #Get original row or column
        originalVector <- originalTable[originalVectorIndex,]

        #Create new rows to store manual allocation values (all other values initiated to NA)
        manualAllocVector <- data.frame(matrix(ncol = ncol(originalTable), nrow = length(newSectorCodes)))
        
        #Assign correct column and row names to new rows dataframe
        colnames(manualAllocVector) <- names(originalVector)
        rownames(manualAllocVector) <- newSectorCodes
        
        #Assign lookup index for allocPercentages vector 
        allocPercentagesRowIndex <- 2
        allocPercentagesColIndex <- 1
        
        defaultPercentages <- getDefaultAllocationPercentages(disagg$UseFileDF, disagg,
                                                            numNewSectors, output='Commodity')
        
        #Create new rows to store default allocation values by copying the original row a number of times equal to the number of new sectors
        defaultAllocVector <- rbind(originalVector, originalVector[rep(1,numNewSectors-1),])
        #multiply all elements in row by default percentages to obtain default allocation values
        defaultAllocVector <- defaultAllocVector*defaultPercentages[,1]
        
        #Assign correct column and row names to new rows dataframe
        colnames(defaultAllocVector) <- names(originalVector)
        rownames(defaultAllocVector) <- newSectorCodes
        '''
    elif (vector_to_disagg in ["UseCol", "ValueAdded"]):
        logging.debug(f"Code not implemented for vector_to_disagg == {vector_to_disagg}")
        sys.exit()
        '''
        #Get commodity and/or industry indeces corresponding to the original sector code
        originalVectorIndex <- which(colnames(originalTable)==disagg$OriginalSectorCode)
        #Get original row or column
        originalVector <- originalTable[,originalVectorIndex, drop = FALSE]

        #Create new cols to store allocation values (all other values initiated to NA)
        manualAllocVector <- data.frame(matrix(ncol = length(newSectorCodes), nrow = nrow(originalTable)))
        
        #Assign correct column and row names to new rows dataframe
        colnames(manualAllocVector) <- newSectorCodes
        rownames(manualAllocVector) <- rownames(originalVector)
        
        #Assign lookup index for allocPercentages vector 
        allocPercentagesRowIndex <- 2
        allocPercentagesColIndex <- 1
        
        defaultPercentages <- getDefaultAllocationPercentages(disagg$UseFileDF, disagg,
                                                            numNewSectors, output='Industry')
        
        #Create new columns to store default allocation values by copying the original column a number of times equal to the number of new sectors
        defaultAllocVector <- cbind(originalVector, originalVector[,rep(1,numNewSectors-1)])
        #multiply all elements in row by default percentages to obtain default allocation values
        defaultAllocVector <- data.frame(t(t(defaultAllocVector)*defaultPercentages[,1]))
        
        #Assign correct column and row names to new rows dataframe
        colnames(defaultAllocVector) <- newSectorCodes
        rownames(defaultAllocVector) <- rownames(originalVector)
        '''

    elif (vector_to_disagg == "UseIntersection"):

        intersction = original_table.loc[originalSectorCode,originalSectorCode]
        print(intersction)
        logging.debug("WORKING HERE")
        sys.exit()
        '''
        intersection <- originalTable[which(rownames(originalTable)==disagg$OriginalSectorCode),
                                  which(colnames(originalTable)==disagg$OriginalSectorCode), drop=FALSE]
    
        defaultPercentages <- getDefaultAllocationPercentages(disagg$UseFileDF, disagg,
                                                            numNewSectors, output='Industry')
        
        defaultAllocVector <- calculateDefaultIntersection(intersection, defaultPercentages, newSectorCodes)

        manualAllocVector <- createBlankIntersection(newSectorCodes)
        
        #Assign lookup index for allocPercentages vector 
        allocPercentagesRowIndex <- 1
        allocPercentagesColIndex <- 2
        '''
        logging.debug(f"Code not implemented for vector_to_disagg == {vector_to_disagg}")
        sys.exit()

    else:
        logging.error(f"Invalid argument for vector_to_disagg: {vector_to_disagg}")
        sys.exit()
    
    '''

  #These different if blocks are needed because of the different dimensions of the manual and default allocation vectors needed for disaggregating 
  #the Make and Use rows and columns. Each block initializes the manual and default allocation values for the relevant rows or columns.
  if(vectorToDisagg == "MakeRow") {
    
  } else if(vectorToDisagg == "MakeCol") {
    
    
  } else if(vectorToDisagg == "MakeIntersection") {
        
  } else if(vectorToDisagg == "UseRow" || vectorToDisagg == "FinalDemand" ) {
    
    
    
  } else if (vectorToDisagg == "UseCol" || vectorToDisagg == "ValueAdded") {
    
    
  } else if(vectorToDisagg == "UseIntersection") {

    
    
  } else {
    #todo error handling
  }
  
  if(nrow(allocPercentages)>0) {
    #Check that there are manual allocations to perform
    #Loop to assign the manual allocations
    for (r in 1:nrow(allocPercentages)) {
      
      #Get data from current row of the data imported from the yml file. 
      rowAlloc <- allocPercentages[r,allocPercentagesRowIndex]
      colAlloc <- allocPercentages[r,allocPercentagesColIndex]
      allocationValue <- allocPercentages[r,3]
      
      #Get the indeces where the allocated values go in new disaggregated rows
      rowAllocIndex <- which(rownames(manualAllocVector)==rowAlloc)
      colAllocIndex <- which(colnames(manualAllocVector)==colAlloc)
      
      #Check for indexing errors
      if(length(rowAllocIndex)==0L) {
        logging::logdebug(paste("rowAlloc not found, no allocation made for row", rowAlloc, sep=" ", "in table."))
      }

      if(length(colAllocIndex)==0L) {
        logging::logdebug(paste("colAlloc not found, no allocation made for column", colAlloc, sep=" ", "in table."))
      }
      
      #Calculate value based on allocation percent
      if(vectorToDisagg == "MakeRow" || vectorToDisagg == "UseRow" || vectorToDisagg == "FinalDemand") {
        value <- originalVector[colAllocIndex]*allocationValue
      } else if(vectorToDisagg=="MakeCol" || vectorToDisagg=="UseCol" || vectorToDisagg == "ValueAdded") {
        value <- originalVector[rowAllocIndex, 1, drop = FALSE]*allocationValue #to keep value as a dataframe
      } else if(vectorToDisagg == "MakeIntersection" || vectorToDisagg=="UseIntersection") {
        value <- intersection[1, 1, drop = FALSE]*allocationValue #to keep value as a dataframe. Should be a 1x1 DF
      }
      
      #If either rowAlloc or column are not valid values, set value to 0 to avoid a runtime error
      if(ncol(value)==0) {
        value <- 0
      }
      #Assign value to correct index
      manualAllocVector[rowAllocIndex, colAllocIndex] <- value
    }
  } else {
    logging::logdebug(paste("rowAlloc not found, no allocation made for", vectorToDisagg, sep=" "))
  }

  #replace all NAs with 0
  manualAllocVector[is.na(manualAllocVector)] <-0
  
  #Replace values in the default allocation vector with values from the Manual allocation vector to finalize the vector disaggregation.

  if(vectorToDisagg == "MakeRow"|| vectorToDisagg == "MakeIntersection" || vectorToDisagg=="UseRow" || vectorToDisagg =="UseIntersection" || vectorToDisagg == "FinalDemand") {
    #assumption is that all columns where there was a manual allocation sum up to the value in the original row/column index.
    manualIndeces <- data.frame(which(colSums(manualAllocVector) !=0 ))
    
    if(nrow(manualIndeces) > 0) {
      for (i in 1:nrow(manualIndeces)) {
        #replace values from manual allocation into default allocation
        tempVector <- manualAllocVector[, manualIndeces[i,1], drop=FALSE]
        defaultAllocVector[, manualIndeces[i,1]] <- tempVector
      }
    }

  } else if (vectorToDisagg == "MakeCol" || vectorToDisagg == "UseCol" || vectorToDisagg == "ValueAdded") {
    #assumption is that all rows where there was a manual allocation sum up to the value in the original row/column index.
    manualIndeces <- data.frame(which(rowSums(manualAllocVector) !=0 ))
    
    if(nrow(manualIndeces) > 0) {
      for (i in 1:nrow(manualIndeces)) {
        #replace values from manual allocation into default allocation
        tempVector <- manualAllocVector[manualIndeces[i,1], , drop=FALSE]
        defaultAllocVector[manualIndeces[i,1],] <- tempVector
      }
    }

  } else {
    manualIndeces <- NA #temporary values 
  }

  return(defaultAllocVector)
    '''
    logging.debug("Function under construction")
    sys.exit()

def get_default_allocation_percentages(file_df, disagg, num_new_sectors, output):
    '''
    #' Obtain a vector of allocation percentages from the specified source file based on disaggregations specifications.
#' @param FileDF dataframe of Make or Use disaggregation data
#' @param disagg Specifications for disaggregating the current Table
#' @param numNewSectors Int. Number of new sectors in the disaggregation
#' @param output String indicating whether allocation values should reference "Commodity" or "Industry" outputs by default
#' @return vector of allocation percentages
    '''
    logging.debug("Function not implemented")
    sys.exit()

def create_blank_intersection(new_sector_codes):
    '''
    #' Creates an empty dataframe matrix of disaggregated sectors.
#' @param newSectorCodes vector of named disaggregated sectors
#' @return square dataframe matrix with new sectors as row and column names
    '''
    logging.debug("Function not implemented")
    sys.exit()

def calculate_default_intersection(original_intersection, default_percentages, new_sector_codes):
    '''
    #' Creates a square dataframe matrix with values assigned based on default percentages
#' @param originalIntersection int value of the original intersection to be disaggregated
#' @param defaultPercentages vector of allocation percentages
#' @param newSectorCodes vector of named disaggregated sectors
#' @return square dataframe matrix with new sectors as row and column names with default values
    '''
    logging.debug("Function not implemented")
    sys.exit()

def get_disagg_industry_percentages(disagg):
    '''
    #' Obtain default disaggregation percentages for industries from the disaggregation input files. 
#' @param disagg Specifications for disaggregating the current Model
#' @return A dataframe with the default disaggregation percentages for the Industries of the current model
    '''
    logging.debug("Function not implemented")
    sys.exit()

def get_disagg_commodity_percentages(disagg):
    '''
    #' Obtain default disaggregation percentages for commodities from the disaggregation input files. 
#' @param disagg Specifications for disaggregating the current Model
#' @return A dataframe with the default disaggregation percentages for the Commodities of the current model
    '''
    logging.debug("Function not implemented")
    sys.exit()

def balance_disagg(model, disagg):
    '''
    #' Balance the Make and Use tables after disaggregation.
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return model object with RAS-balanced disaggregation sectors 
    '''
    logging.debug("Function not implemented")
    sys.exit()

def build_disagg_full_use(model, disagg):
    '''
    #' Build a Full Use table using the Use transactions, Use value added, and final demand model objects
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return dataframe representing a use table that includes the Use transactions, Use value added, and final demand sectors 
    '''
    logging.debug("Function not implemented")
    sys.exit()

def calculate_balanced_domestic_tables(model, disagg, balanced_full_use):
    '''
    #' Calculate the domestic use transactions and final demand tables after RAS balancing
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param balancedFullUse A fullUse table (including UseTransactions, UseValueAdded, and FinalDemand), created to determine whether RAS balancing is needed
#' @return list containing balanced domesticFinalDemand and domesticUseTransactions dataframes. 
    '''
    logging.debug("Function not implemented")
    sys.exit()
