# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def aggregate_model(model):
    '''
    #' Aggregate a model based on specified source file
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return An aggregated model.
    '''
    pass

def get_aggregation_specs(model, config_paths = None):
    '''
    #' Obtain aggregation specs from input files
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @param configpaths str vector, paths (including file name) of agg configuration file(s).
    #' If NULL, built-in config files are used.
    #' @return A model with the specified aggregation and disaggregation specs.
    '''
    pass

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