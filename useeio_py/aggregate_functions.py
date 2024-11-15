# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from . import (load_io_tables, configuration_functions)
from .utility_functions import get_index
import sys

#TODO make sure that functions that return model object in R return
#  model object in python code. Don't assume inplace modification of model.


#Done
def aggregate_model(model: "USEEIOModel"):
    '''
    Aggregate a model based on specified source file
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return An aggregated model.
    '''
    logging.info("Initializing Aggregation of IO tables...")
    for aggSpecKey in model.AggregationSpecs:
        aggSpec = model.AggregationSpecs[aggSpecKey]
        # aggregating economic tables
        model.MakeTransactions = aggregate_make_table(model, aggSpec)
        model.UseTransactions = aggregate_use_table(model, aggSpec)
        model.DomesticUseTransactions = aggregate_use_table(model, aggSpec, domestic = True)
        model.UseValueAdded = aggregate_va(model, aggSpec)

        ### These lines all marked as todo in R code...###
        # model.FinalDemand = aggregate_fd(model, aggSpec) #TODO
        # model.DomesticFinalDemand = aggregate_fd(model, aggSpec, domestic = True) #TODO
        # model.MarginSectors = aggregate_margin_sectors(model, aggSpec) #TODO
        # model.Margins = aggregate_margins(model, aggSpec) #TODO

        # model.ValueAddedMeta = aggregate_va_meta(model, aggSpec) #TODO
        # model.FinalDemandMeta = aggregate_fd_meta(model, aggSpec) #TODO
        ##################################################

        # aggregating Crosswalk
        model.crosswalk = aggregate_master_crosswalk(model, aggSpec)
        # obtaining indices to aggregate sectors in remaining model objects
        agg = aggSpec['Sectors']
        mainComIndex = get_index(model.Commodities['Code_Loc'], agg[0]) # first item in Aggregation is the sector to aggregate to, not to be removed
        mainIndIndex = get_index(model.Industries['Code_Loc'], agg[0])
        comIndicesToAggregate_bool = model.Commodities['Code_Loc'].isin(agg[1:]) # find com indeces containing references to the sectors to be aggregated
        indIndicesToAggregate_bool = model.Industries['Code_Loc'].isin(agg[1:]) # find ind indeces containing references to the sectors to be aggregated
        indIndicesToAggregate = model.Industries.loc[indIndicesToAggregate_bool,"Code_Loc"]
        comIndicesToAggregate = model.Commodities.loc[comIndicesToAggregate_bool,"Code_Loc"]

        # aggregating (i.e. removing) sectors from model lists
        # aggregate Industry lists
        if(sum(indIndicesToAggregate_bool) > 0):
            model.Industries = model.Industries.loc[~indIndicesToAggregate_bool]
            model.MultiYearIndustryCPI = aggregate_multi_year_cpi(model, mainIndIndex, indIndicesToAggregate, "Industry")
            model.MultiYearIndustryOutput = aggregate_multi_year_output(model.MultiYearIndustryOutput, mainIndIndex, indIndicesToAggregate)
        
        # aggregate Commodity lists
        if(sum(comIndicesToAggregate_bool) > 0):
            model.Commodities = model.Commodities.loc[~comIndicesToAggregate_bool]
            model.MultiYearCommodityCPI = aggregate_multi_year_cpi(model, mainIndIndex, indIndicesToAggregate, "Commodity")
            model.MultiYearCommodityOutput = aggregate_multi_year_output(model.MultiYearIndustryOutput, mainComIndex, comIndicesToAggregate)
            #model.ImportCosts = aggregate_import_costs(model.Commodities, comIndicesToAggregate) #TODO: marked as todo in useeior code

        load_io_tables.calculate_industry_commodity_output(model)

    # return(model)

#TODO: test implementation
def get_aggregation_specs(model: "USEEIOModel", config_paths = None):
    '''
    #' Obtain aggregation specs from input files
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @param configpaths str vector, paths (including file name) of agg configuration file(s).
    #' If NULL, built-in config files are used.
    #' @return A model with the specified aggregation and disaggregation specs.
    '''
    model.AggregationSpecs = dict()
    for configFile in model.specs['AggregationSpecs']: # is this right?
        logging.info(f"Loading aggregation specification file for {configFile}...")
        config = configuration_functions.get_configuration(configFile, "agg", config_paths)
        if('Aggregation' in config.keys()):
            for key in config['Aggregation']:
                model.AggregationSpecs[key] = config["Aggregation"][key]
    # return(model)

def aggregate_sectors_in_tbs(model: "USEEIOModel", aggregation_specs: dict, sat_table, sat):
    '''
    #' Aggregate satellite tables from static file based on specs
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param aggregationSpecs Specifications for aggregation
    #' @param sattable A standardized satellite table with resource and emission names from original sources.
    #' @param sat The abbreviation for the satellite table.
    #' @return A standardized satellite table with aggregated sectors added.
    '''
    logging.debug("Function not implemented")
    sys.exit()

#DONE
def aggregate_multi_year_cpi(model: "USEEIOModel", main_index:int, indices_to_aggregate:"Series", cpi_type:str):
    '''
    #' Aggregate MultiYear CPI model objects
    #' @param model An EEIO model object with model specs and IO tables loaded.
    #' @param mainIndex Index to aggregate the others to.
    #' @param indecesToAggregate List of indeces to aggregate.
    #' @param type String to designate either commodity or industry
    #' @return newCPI A dataframe with the aggregatded CPI values by year.
    '''
    if cpi_type == "Industry":
        originalCPI = model.MultiYearIndustryCPI
        originalOutput = model.MultiYearIndustryOutput
    else:
        originalCPI = model.MultiYearCommodityCPI
        originalOutput = model.MultiYearCommodityOutput
    
    newCPI = originalCPI.copy(deep=True)
    aggOutputs = originalOutput.iloc[main_index] + originalOutput.loc[indices_to_aggregate].sum(axis=0)

    mainIndexOutputRatios = originalOutput.iloc[main_index] / aggOutputs
    aggIndecesOutputRatios = originalOutput.loc[indices_to_aggregate]/aggOutputs

    newCPI.iloc[main_index] = newCPI.iloc[main_index]*mainIndexOutputRatios + \
        (newCPI.loc[indices_to_aggregate]*aggIndecesOutputRatios).sum(axis=0)
    newCPI = remove_rows_from_list(newCPI, indices_to_aggregate)
    return(newCPI)


#DONE
def aggregate_make_table(model: "USEEIOModel", aggregation_specs: dict):
    '''
    Aggregate the MakeTable based on specified source file.

    Parameters
    ----------
    model : USEEIOModel
        An EEIO model object with model specs and IO tables loaded.
    aggregationSpecs : dict
        Specifications for aggregation
    
    Returns
    -------
    DataFrame
        An aggregated MakeTable.
    '''
    agg = aggregation_specs['Sectors']
    for sector in agg[1:]: # First sector in list is the one we are aggregating to, so skip
        model.MakeTransactions = aggregate_sector(model, agg[0], sector, "Make")
    
    agg = agg[1:]
    model.MakeTransactions = model.MakeTransactions.drop(agg, axis = 0, errors = "ignore")
    model.MakeTransactions = model.MakeTransactions.drop(agg, axis = 1, errors = "ignore")

    return(model.MakeTransactions)


#DONE
def aggregate_use_table(model: "USEEIOModel", aggregation_specs: dict, domestic: bool = False):
    '''
    Aggregate the UseTable based on specified source file.

    Parameters
    ----------
    model : USEEIOModel
        An EEIO model object with model specs and IO tables loaded.
    aggregationSpecs : dict
        Specifications for aggregation
    domestic : bool
        A logical value indicating whether to aggregate final demand.
    
    Returns
    -------
    DataFrame
        An aggregated UseTable.
    '''
    agg = aggregation_specs['Sectors']
    for sector in agg[1:]: # First sector in list is the one we are aggregating to, so skip
        if domestic:
            model.DomesticUseTransactions = aggregate_sector(model, agg[0], sector, "Use", domestic=domestic)
        else:
            model.UseTransactions = aggregate_sector(model, agg[0], sector, "Use", domestic=domestic)

    agg = agg[1:]

    if domestic:
        model.DomesticUseTransactions = model.DomesticUseTransactions.drop(agg, axis = 0, errors = "ignore")
        model.DomesticUseTransactions = model.DomesticUseTransactions.drop(agg, axis = 1, errors = "ignore")

        return(model.DomesticUseTransactions)
    else:
        model.UseTransactions = model.UseTransactions.drop(agg, axis = 0, errors = "ignore")
        model.UseTransactions = model.UseTransactions.drop(agg, axis = 1, errors = "ignore")

        return(model.UseTransactions)

#DONE
def aggregate_va(model: "USEEIOModel", aggregation_specs: dict):
    '''
    Aggregate the ValueAdded based on specified source file.

    Parameters
    ----------
    model : USEEIOModel
        An EEIO model object with model specs and IO tables loaded.
    aggregationSpecs : dict
        Specifications for aggregation
    
    Returns
    -------
    DataFrame
        An aggregated UseValueAddedTable.
    '''
    agg = aggregation_specs['Sectors']
    for sector in agg[1:]: # First sector in list is the one we are aggregating to, so skip
        model.UseValueAdded = aggregate_sector(model, agg[0], sector, "VA")

    agg = agg[1:]
    
    model.UseValueAdded = model.UseValueAdded.drop(agg, axis = 0, errors = "ignore")
    model.UseValueAdded = model.UseValueAdded.drop(agg, axis = 1, errors = "ignore")

    return(model.UseValueAdded)

#DONE
def aggregate_sector(model: "USEEIOModel", main_sector:str, sector_to_remove:str, table_type:str, domestic:bool=False):
    '''
    Aggregate a sector in a table

    Parameters
    ----------
    model : USEEIOModel
        An EEIO model object with model specs and IO tables loaded
    main_sector : str
        Sector to aggregate to
    sector_to_remove : str
        Sector to be aggregated into mainSector, then removed from table
    table_type : {'Use', 'Make', 'VA'}
        String to designate either Make, Use, or Value Added table
    domestic : bool, default=False
        Boolean to indicate whether to aggregate the UseTransactions or DomesticUseTransactions table 
    
    Returns
    -------
    type
        aggregated table 
    '''
    if table_type == "Use":
        mainRowIndex = get_index(model.Commodities['Code_Loc'], main_sector)
        mainColIndex = get_index(model.Industries['Code_Loc'], main_sector)

        removeRowIndex = get_index(model.Commodities['Code_Loc'], sector_to_remove)
        removeColIndex = get_index(model.Industries['Code_Loc'], sector_to_remove)
        table = model.DomesticUseTransactions if domestic else model.UseTransactions
    elif table_type == "Make":
        mainRowIndex = get_index(model.Industries['Code_Loc'], main_sector)
        mainColIndex = get_index(model.Commodities['Code_Loc'], main_sector)
        removeRowIndex = get_index(model.Industries['Code_Loc'], sector_to_remove)
        removeColIndex = get_index(model.Commodities['Code_Loc'], sector_to_remove)
        table = model.MakeTransactions
    elif table_type == "VA":
        mainRowIndex = get_index(model.ValueAddedMeta['Code_Loc'], main_sector)
        mainColIndex = get_index(model.Industries['Code_Loc'], main_sector)
        removeRowIndex = get_index(model.ValueAddedMeta['Code_Loc'], sector_to_remove)
        removeColIndex = get_index(model.Industries['Code_Loc'], sector_to_remove)
        table = model.UseValueAdded
    else:
        sys.exit("Invalid table_type")

    if(removeRowIndex != -1 and mainRowIndex != -1): # If there is a row to remove and merge with main sector
        table.iloc[mainRowIndex,:] = table.iloc[mainRowIndex,:] + table.iloc[removeRowIndex,:] # add rows together
        table.iloc[removeRowIndex,:] = 0
    
    if(removeColIndex != -1 and mainColIndex != -1): # If there is a row to remove and merge with main sector
        table.iloc[:,mainColIndex] = table.iloc[:,mainColIndex] + table.iloc[:,removeColIndex] # add rows together
        table.iloc[:,removeColIndex] = 0

    return(table)


def aggregate_master_crosswalk(model: "USEEIOModel", aggregation_specs: dict):
    '''
    #' Aggregate the MasterCrosswalk on the selected sectors
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param aggregationSpecs Specifications for aggregation
    #' @return crosswalk with aggregated sectors removed
    '''
    agg = aggregation_specs['Sectors']
    secLength = len(agg[0].split("/")[0])
    agg_filter = [a[0:secLength] for a in agg]

    new_cw = model.crosswalk.copy(deep=True)
    x = new_cw.loc[new_cw['USEEIO'] == (agg_filter[0])].BEA_Sector.iloc[0]
    y = new_cw.loc[new_cw['USEEIO'] == (agg_filter[0])].BEA_Summary.iloc[0]
    new_cw.loc[new_cw['USEEIO'].isin(agg_filter[1:]),"BEA_Sector"] = x
    new_cw.loc[new_cw['USEEIO'].isin(agg_filter[1:]),"BEA_Summary"] = y

    return(new_cw)

def remove_rows_from_list(sector_list: "DataFrame", indices_to_aggregate: "Index"):
    '''
    #' Remove specific rows from the specified list object in the model
    #' @param sectorList Model object to be aggregated 
    #' @param indecesToAggregate List of indeces of sectors to remove from list (i.e. aggregated sectors)
    #' @return An aggregated sectorList
    '''
    return(sector_list.drop(indices_to_aggregate, errors = "ignore"))

def aggregate_multi_year_output(original_output:"DataFrame", main_index, indices_to_aggregate):
    '''
    #' Aggregate MultiYear Output model objects
    #' @param originalOutput MultiYear Output dataframe
    #' @param mainIndex Index to aggregate the others to.
    #' @param indecesToAggregate List of indeces to aggregate.
    #' @return model A dataframe with the disaggregated GDPGrossOutputIO by year.
    '''
    new_output = original_output.copy(deep=True)
    new_output.iloc[main_index] = original_output.iloc[main_index] + original_output.loc[indices_to_aggregate].sum(axis=0)
    new_output = new_output.drop(indices_to_aggregate, axis=0, errors="ignore")
    return(new_output)