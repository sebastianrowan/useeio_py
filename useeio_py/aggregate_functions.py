# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
import load_io_tables
import configuration_functions

#TODO: Update function documentation

#TODO: test implementation
def aggregate_model(model):
    '''
    #' Aggregate a model based on specified source file
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return An aggregated model.
    '''
    logging.info("Initializing Aggregation of IO tables...")
    for aggSpec in model.AggregationSpecs:
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
        agg = aggSpec['Spectors']

        mainComIndex = get_index(model.Commodities['Code_Loc'], agg[0]) # #first item in Aggregation is the sector to aggregate to, not to be removed

        mainIndIndex = get_index(model.Industries['Code_Loc'], agg[0])
        comIndicesToAggregate = np.where(model.Commodities['Code_Loc'].isin(agg[1:]))  # find com indeces containing references to the sectors to be aggregated
        indIndicesToAggregate = np.where(model.Industries['Code_Loc'].isin(agg[1:]))  # find ind indeces containing references to the sectors to be aggregated

        # aggregating (i.e. removing) sectors from model lists
        # aggregate Industry lists
        if(len(indIndicesToAggregate) != 0):
            model.Industries = remove_rows_from_list(model.Industries, indIndicesToAggregate)
            model.MultiYearIndustryCPI = aggregate_multi_year_cpi(model, mainIndIndex, indIndicesToAggregate, "Industry")
            model.MultiYearIndustryOutput = aggregate_multi_year_output(model.MultiYearIndustryOutput, mainIndIndex, indIndicesToAggregate)
        
        # aggregate Commodity lists
        if(len(comIndicesToAggregate) != 0):
            model.Commodities = remove_rows_from_list(model.Industries, comIndicesToAggregate)
            model.MultiYearCommodityCPI = aggregate_multi_year_cpi(model, mainIndIndex, indIndicesToAggregate, "Commodity")
            model.MultiYearCommodityOutput = aggregate_multi_year_output(model.MultiYearIndustryOutput, mainComIndex, comIndicesToAggregate)
            #model.ImportCosts = aggregate_import_costs(model.Commodities, comIndicesToAggregate) #TODO: marked as todo in useeior code

        model = load_io_tables.calculate_industry_commodity_output(model)

    return(model)

#TODO: test implementation
def get_aggregation_specs(model, config_paths = None):
    '''
    #' Obtain aggregation specs from input files
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @param configpaths str vector, paths (including file name) of agg configuration file(s).
    #' If NULL, built-in config files are used.
    #' @return A model with the specified aggregation and disaggregation specs.
    '''
    model.AggregationSpecs = list()
    for configFile in model.specs['AggregationSpecs']: # is this right?
        logging.info(f"Loading aggregation specification file for {configFile}...")
        config = configuration_functions.get_configuration(configFile, "agg", config_paths)
        if('Aggregation' in config['names']):
            model.AggregationSpecs.append(config['Aggregation'])
    
    return(model)

def aggregate_sectors_in_tbs(model, aggregation_specs, sat_table, sat):
    '''
    #' Aggregate satellite tables from static file based on specs
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param aggregationSpecs Specifications for aggregation
    #' @param sattable A standardized satellite table with resource and emission names from original sources.
    #' @param sat The abbreviation for the satellite table.
    #' @return A standardized satellite table with aggregated sectors added.
    '''
    pass

def aggregate_multi_year_cpi(model, main_index, indices_to_aggregate, type):
    '''
    #' Aggregate MultiYear CPI model objects
    #' @param model An EEIO model object with model specs and IO tables loaded.
    #' @param mainIndex Index to aggregate the others to.
    #' @param indecesToAggregate List of indeces to aggregate.
    #' @param type String to designate either commodity or industry
    #' @return newCPI A dataframe with the aggregatded CPI values by year.
    '''
    pass

#TODO: rewrite this function to use matrix calculations when possible
def aggregate_make_table(model, aggregation_specs):
    '''
    #' Aggregate the MakeTable based on specified source file
    #' @param model An EEIO model object with model specs and IO tables loaded.
    #' @param aggregationSpecs Specifications for aggregation
    #' @return An aggregated MakeTable.
    '''
    pass

#TODO: rewrite this function to use matrix calculations when possible
def aggregate_use_table(model, aggregation_specs, domestic = False):
    '''
    #' Aggregate the UseTable based on specified source file
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @param aggregationSpecs Specifications for aggregation
    #' @param domestic Boolean to indicate whether to aggregate the UseTransactions or DomesticUseTransactions table 
    #' @return An aggregated UseTransactions or DomesticUseTransactions Table.
    '''
    pass

#TODO: rewrite this function to use matrix calculations when possible
def aggregate_va(model, aggregation_specs):
    '''
    #' Aggregate the MakeTable based on specified source file
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param aggregationSpecs Specifications for aggregation
    #' @return An aggregated MakeTable.
    '''
    pass

def aggregate_sector(model, main_sector, sector_to_remove, table_type, domestic = False):
    '''
    #' Aggregate a sector in a table
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @param mainSector  Sector to aggregate to (string)
    #' @param sectorToRemove Sector to be aggregated into mainSector, then removed from table (string)
    #' @param tableType String to designate either Make or Use table
    #' @param domestic Boolean to indicate whether to aggregate the UseTransactions or DomesticUseTransactions table 
    #' @return aggregated table 
    '''
    pass

def get_index(sector_list, sector):
    '''
    #' Return the index where a sector occurrs in a sectorList 
    #' @param sectorList Dataframe (of strings) to match the index of the sector param
    #' @param sector String of the sector to look the index for
    #' @return Index of sector in sectorList
    '''
    pass

def aggregate_master_crosswalk(model, aggregation_specs):
    '''
    #' Aggregate the MasterCrosswalk on the selected sectors
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param aggregationSpecs Specifications for aggregation
    #' @return crosswalk with aggregated sectors removed
    '''
    pass

def remove_rows_from_list(sector_list, indices_to_aggregate):
    '''
    #' Remove specific rows from the specified list object in the model
    #' @param sectorList Model object to be aggregated 
    #' @param indecesToAggregate List of indeces of sectors to remove from list (i.e. aggregated sectors)
    #' @return An aggregated sectorList
    '''
    pass

def aggregate_multi_year_output(original_output, main_index, indices_to_aggregate):
    '''
    #' Aggregate MultiYear Output model objects
    #' @param originalOutput MultiYear Output dataframe
    #' @param mainIndex Index to aggregate the others to.
    #' @param indecesToAggregate List of indeces to aggregate.
    #' @return model A dataframe with the disaggregated GDPGrossOutputIO by year.
    '''
    pass