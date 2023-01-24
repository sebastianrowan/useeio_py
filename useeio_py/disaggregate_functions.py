# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def disaggregate_model(model):
    '''
    #' Disaggregate a model based on specified source file
#' @param model An EEIO model object with model specs and IO tables loaded
#' @return A disaggregated model.
    '''
    pass

def get_disaggregation_specs(model, config_paths = None):
    '''
    #' Obtain aggregation and disaggregation specs from input files
#' @param model An EEIO model object with model specs and IO tables loaded
#' @param configpaths str vector, paths (including file name) of disagg configuration file(s).
#' If NULL, built-in config files are used.
#' @return A model with the specified aggregation and disaggregation specs.
    '''
    pass

def disaggregate_setup(model, config_paths = None):
    '''
    #' Setup the configuration specs based on the input files
#' @param model An EEIO model object with model specs and IO tables loaded
#' @param configpaths str vector, paths (including file name) of disagg configuration file(s).
#' If NULL, built-in config files are used.
#' @return A model object with the correct disaggregation specs.
    '''
    pass

def prepare_two_region_disaggregation(disagg, region, regions):
    '''
    #' Generate two-region disaggregation specs from a national spec
#' @param disagg Specifications for disaggregating the current Table
#' @param region Str, Location code for target disaggregation specs
#' @param regions list of location codes from ModelRegionAcronyms
#' @return modified disagg specs for target region
    '''
    pass

def disaggregateInternationalTradeAdjustment(model, disagg, ratios = None, adjustmentByCommodity = False):
    '''
    #' Disaggregate model$InternationalTradeAdjustments vector in the main model object
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param ratios Specific ratios to be used for the disaggregation of the InternationalTradeAdjusment object in place of using economic totals to derive the ratios.
#' @param adjustmentByCommodity Flag to denote whether to disaggregate the InternationalTradeAdjustmentbyCommodity object which is only present in industry models
#' @return newInternationalTradeAdjustment A vector which contains the InternationalTradeAdjustment for the disaggregated sectors
    '''
    pass

def disaggregate_margins(model, disagg):
    '''
    #' Disaggregate model$Margins dataframe in the main model object
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return newMargins A dataframe which contain the margins for the disaggregated sectors
    '''
    pass

def disaggregated_ratios(model, disagg, output_type = "Commodity"):
    '''
    #' Calculate ratios of throughputs from the disaggregated sectors
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param output_type A string value indicating whether to obtain "Commodity" or "Industry" ratios
#' @return disaggRatios A dataframe which contain the disaggregated ratios for the disaggregated sectors
    '''
    pass

def disaggregate_sector_dfs(model, disagg, list_type):
    '''
    #' Disaggregate model$Commodity or model$Industry dataframes in the main model object
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param list_type string indicating whether to disaggregate model$Industry or model$Commodity dataframe. 
#' @return newSectors A dataframe which contain the disaggregated model$Commodity or model$Industry objects
    '''
    pass

def disaggregate_satellite_subset_by_ratio(sat_table, disagg, allocating_sectors, allocation_vector = None):
    '''
    #' Disaggregate a portion of a satellite table based on an allocation_vector
#' @param sattable A standardized satellite table to be disaggregated.
#' @param disagg Specifications for disaggregating the current Table
#' @param allocating_sectors vector of sectors to allocate to
#' @param allocation_vector named vector of allocation ratios
#' @return A satellite table with new sectors added.
    '''
    pass

def disaggregate_satellite_table(disagg, tbs, sat_spec):
    '''
    #' Disaggregate satellite tables from static file based on specs
#' @param disagg Specifications for disaggregating the current Table
#' @param tbs A standardized satellite table with resource and emission names from original sources.
#' @param sat_spec, a standard specification for a single satellite table.
#' @return A standardized satellite table with old sectors removed and new sectors added.
    '''
    pass

def disaggregate_make_table(model, disagg):
    '''
    #' Disaggregate make table based on specs
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return A standardized make table with old sectors removed and new sectors added.
    '''
    pass

def disaggregate_use_table(model, disagg, domestic = False):
    '''
    #' Disaggregate Use table based on specs
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param domestic A logical value indicating whether to disaggregate domestic final demand.
#' @return A standardized make table with old sectors removed and new sectors added.
    '''
    pass

def disaggregate_final_demand(model, disagg, domestic = False):
    '''
    #' Disaggregate Final Demand based on specs
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param domestic A logical value indicating whether to disaggregate domestic final demand.
#' @return A standardized final demand table with old sectors removed and new sectors with manual and default allocations added.
    '''
    pass

def disaggregate_va(model, disagg):
    '''
    #' Disaggregate Value Added based on specs
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return A standardized Vale Added table with old sectors removed and new sectors with manual and default allocations added.
    '''
    pass

def uniform_disagg(model, disagg, table):
    '''
    #' Disaggregate make or use table uniformly based on the number of new sectors
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param table DataFrame of make or use table
#' @return A standardized make table with old sectors removed and new, uniformly disaggregated sectors added.
    '''
    pass

def disaggregate_rows(row_vectors, disagg_specs, duplicate=False, not_uniform = False):
    '''
    #' Disaggregate multiple rows from a table.
#' @param RowVectors A dataframe containing the rows to disaggregate
#' @param disagg_specs Specifications for disaggregating the current Table
#' @param duplicate A flag that indicates whether the disaggregated rows are to be duplicated or not (e.g. for CPI values)
#' @param notUniform A flag that indicates whether the disaggregated rows are to be disaggregated in uniform manner or not
#' @return A dataframe with disaggregated rows.
    '''
    pass

def disaggregate_cols(col_vectors, disagg_specs, duplicate=False, not_uniform = False):
    '''
    #' Disaggregate multiple columns from a table.
#' @param ColVectors A dataframe containing the columns to disaggregate
#' @param disagg_specs Specifications for disaggregating the current Table
#' @param duplicate A flag that indicates whether the disaggregated columns are to be duplicated or not (e.g. for CPI values)
#' @param notUniform A flag that indicates whether the disaggregated columns are to be disaggregated in uniform manner or not
#' @return A dataframe with disaggregated columns.
    '''
    pass

def disaggregate_row(original_row_vector, disagg_specs, duplicate=False, not_uniform = False):
    '''
    #' Disaggregate a single row from a table.
#' @param originalRowVector A dataframe containing the row to disaggregate
#' @param disagg_specs Specifications for disaggregating the current Table
#' @param duplicate A flag that indicates whether the disaggregated row is to be duplicated or not (e.g. for CPI values)
#' @param notUniform A flag that indicates whether the disaggregated row is to be disaggregated in uniform manner or not
#' @return A dataframe with the original row disaggregated.
    '''
    pass

def disaggregate_col(original_col_vector, disagg_specs, duplicate=False, not_uniform = False):
    '''
    #' Disaggregate a single column from a table.
#' @param originalColVector A dataframe containing the column to disaggregate
#' @param disagg_specs Specifications for disaggregating the current Table
#' @param duplicate A flag that indicates whether the disaggregated columns are to be duplicated or not (e.g. for CPI values)
#' @param notUniform A flag that indicates whether the disaggregated columns are to be disaggregated in uniform manner or not
#' @return A dataframe with the original column disaggregated.
    '''
    pass

def disaggregate_master_crosswalk(model, disagg):
    '''
    #' Disaggregate the MasterCrosswalk to include the new sectors for disaggregation
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return crosswalk with new sectors added.
    '''
    pass

def specified_make_disagg(model, disagg):
    '''
    #' Disaggregate make table based on the allocations specified in the files referenced in the diaggregation specs.
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return A standardized make table with old sectors removed and new disaggregated sectors added based on the allocations in the disaggregation specs.
    '''
    pass

def specified_use_disagg(model, disagg, domestic = False):
    '''
    #' Disaggregate use table based on the allocations specified in the files referenced in the disaggregation specs.
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param domestic Flag that indicates where to use the Domestic Use or UseTransactions table
#' @return A standardized make table with old sectors removed and new disaggregated sectors added based on the allocations in the disaggregation specs.
    '''
    pass

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
    pass

def apply_allocation(disagg, alloc_percentages, vector_to_disagg, original_table):
    '''
    #' Allocate values specified by the .yml disaggregation specs to the correct places in a disaggregated row/column of the Use/Make tables. 
#' @param disagg Specifications for disaggregating the current Table
#' @param allocPercentages Dataframe. A subset of the dataframe that contains the percentages to allocate to specific industry and commodity combinations in the disaggregated vector. Parameter use coordinated with @param vectorToDisagg
#' @param vectorToDisagg String. A parameter to indicate what table and what part of that table is being disaggregated (e.g. "MakeCol" or "Intersection") 
#' @param originalTable Dataframe. The original dataframe upon which allocation is performed (e.g., Make or Use)
#' @return A dataframe with the values specified in the disaggSpecs assigned to the correct Make or Use table indeces.
    '''
    pass

def get_default_allocation_percentages(file_df, disagg, num_new_sectors, output):
    '''
    #' Obtain a vector of allocation percentages from the specified source file based on disaggregations specifications.
#' @param FileDF dataframe of Make or Use disaggregation data
#' @param disagg Specifications for disaggregating the current Table
#' @param numNewSectors Int. Number of new sectors in the disaggregation
#' @param output String indicating whether allocation values should reference "Commodity" or "Industry" outputs by default
#' @return vector of allocation percentages
    '''
    pass

def create_blank_intersection(new_sector_codes):
    '''
    #' Creates an empty dataframe matrix of disaggregated sectors.
#' @param newSectorCodes vector of named disaggregated sectors
#' @return square dataframe matrix with new sectors as row and column names
    '''
    pass

def calculate_default_intersection(original_intersection, default_percentages, new_sector_codes):
    '''
    #' Creates a square dataframe matrix with values assigned based on default percentages
#' @param originalIntersection int value of the original intersection to be disaggregated
#' @param defaultPercentages vector of allocation percentages
#' @param newSectorCodes vector of named disaggregated sectors
#' @return square dataframe matrix with new sectors as row and column names with default values
    '''
    pass

def get_disagg_industry_percentages(disagg):
    '''
    #' Obtain default disaggregation percentages for industries from the disaggregation input files. 
#' @param disagg Specifications for disaggregating the current Model
#' @return A dataframe with the default disaggregation percentages for the Industries of the current model
    '''
    pass

def get_disagg_commodity_percentages(disagg):
    '''
    #' Obtain default disaggregation percentages for commodities from the disaggregation input files. 
#' @param disagg Specifications for disaggregating the current Model
#' @return A dataframe with the default disaggregation percentages for the Commodities of the current model
    '''
    pass

def balance_disagg(model, disagg):
    '''
    #' Balance the Make and Use tables after disaggregation.
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return model object with RAS-balanced disaggregation sectors 
    '''
    pass

def build_disagg_full_use(model, disagg):
    '''
    #' Build a Full Use table using the Use transactions, Use value added, and final demand model objects
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @return dataframe representing a use table that includes the Use transactions, Use value added, and final demand sectors 
    '''
    pass

def calculate_balanced_domestic_tables(model, disagg, balanced_full_use):
    '''
    #' Calculate the domestic use transactions and final demand tables after RAS balancing
#' @param model A complete EEIO model: a list with USEEIO model components and attributes.
#' @param disagg Specifications for disaggregating the current Table
#' @param balancedFullUse A fullUse table (including UseTransactions, UseValueAdded, and FinalDemand), created to determine whether RAS balancing is needed
#' @return list containing balanced domesticFinalDemand and domesticUseTransactions dataframes. 
    '''
    pass
