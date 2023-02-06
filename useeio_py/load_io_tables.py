# -*- coding: utf-8 -*-
'''Functions for loading input-output tables'''

import logging
import importlib.resources
import pandas as pd
from . import (
    utility_functions, io_functions, load_margins, aggregate_functions, disaggregate_functions,
    hybridization_functions, load_go_and_cpi, stateior_functions
)
import numpy as np
import re

#TODO: Test implementation
def load_io_data(model, config_paths = None):
    '''
    Prepare economic components of an EEIO form USEEIO model
    '''
    # Declare model IO objects
    logging.info("Initializing IO tables...")
    # Load model IO meta
    load_io_meta(model)
    # Define IO table names
    io_table_names = [
        "MakeTransactions", "UseTransactions", "DomesticUseTransactions",
        "UseValueAdded", "FinalDemand", "DomesticFinalDemand",
        "InternationalTradeAdjustment"
    ]
    # Load IO data
    if model.specs['IODataSource'] == "BEA":
        io_codes = load_io_codes(model)
        for name in io_table_names:
            setattr(model, name, load_national_io_data(model, io_codes)[name]) 
    elif model.specs['IODataSource'] == "stateior":
        setattr(model, name, load_two_region_state_io_tables(model, io_codes)[name])

    # Add Industry and Commodity Output
    load_commodity_and_industry_output(model)

    # Transform model FinalDemand and DomesticFinalDemand to by-industry form
    if model.specs['CommodityorIndustryType']=='Industry':
        # Keep the orignal FinalDemand (in by-commodity form)
        model.FinalDemandbyCommodity = model.FinalDemand
        model.DomesticFinalDemandbyCommodity = model.DomesticFinalDemand
        model.InternationalTradeAdjustmentbyCommodity = model.InternationalTradeAdjustment
        model.FinalDemand = io_functions.transform_final_demand_with_market_shares(
            model.FinalDemand, model
        ) #TODO
        model.DomesticFinalDemand = io_functions.transform_final_demand_with_market_shares(
            model.DomesticFinalDemand, model
        )
        model.InternationalTradeAdjustment = unlist(io_functions.transform_final_demand_with_market_shares(
            model.InternationalTradeAdjustment, model
        )) # unlist is R function. not sure if it will be necessary to translate
        # will depend on output of transform_final_demand_with_market_shares() function
        model.InternationalTradeAdjustment = model.InternationalTradeAdjustment.set_index(
            model.Industries['Code_Loc']
        )

    # Add Margins Table
    model.Margins = load_margins.get_margins_table(model) #TODO

    # Add Chain Price Index (CPI) to model
    model.MultiYearIndustryCPI = load_go_and_cpi.load_chain_price_index_table(model.specs).loc(model.Industries['Code']) #TODO
    model.MultiYearIndustryCPI = model.MultiYearIndustryCPI.set_index(model.Industries['Code_Loc'])
    
    # Transform industry CPI to commodity CPI
    #TODO: Check this implementation. R Code used a [, FALSE] selection to eliminate all columns here. Not sure how this translates
    model.MultiYearCommodityCPI = model.Commodities.set_index(model.Commodities['Code_Loc'])

    for year_col in model.MultiYearIndustryCPI.columns:
        model.MultiYearCommodityCPI[year_col] = io_functions.transform_industry_cpi_to_commodity_cpi_for_year(
            int(year_col),
            model
        ) #TODO
    
    # Check for aggregation
    if model.specs['AggregationSpecs'] is not None:
        aggregate_functions.get_aggregation_specs(model, config_paths) #TODO
        aggregate_functions.aggregate_model(model) #TODO


    # Check for disaggregation
    if model.specs['DisaggregationSpecs'] is not None:
        disaggregate_functions.get_disaggregation_specs(model, config_paths) #TODO
        disaggregate_functions.disaggregate_model(model) #TODO

    # Check for hybridization
    if model.specs['ModelType'] == "EEIO-IH":
        hybridization_functions.get_hybridization_specs(model, config_paths) #TODO
        hybridization_functions.get_hybridization_files(model, config_paths) #TODO
    
#DONE
def load_io_meta(model):
    '''Prepare metadata of economic components of an EEIO form USEEIO model'''
    io_codes = load_io_codes(model)
    model_base_elements = model.get_elements()

    model.Commodities = pd.merge(
        io_codes['Commodities'],
        pd.read_csv(
            utility_functions.get_named_dataset('useeio_py.inst.extdata', "USEEIO_Commodity_Meta.csv"),
            header = 0
        ),
        how = 'left',
        on = 'Code'
    )
            
    model.Industries = pd.read_parquet(
        utility_functions.get_named_dataset(
            'useeio_py.data',
            f"{model.specs['BaseIOLevel']}_IndustryCodeName_{model.specs['BaseIOSchema']}.parquet"
        )
    )
    
    merge_code_names = [
        "HouseholdDemandCodes","InvestmentDemandCodes","ChangeInventoriesCodes",
        "ExportCodes","ImportCodes","GovernmentDemandCodes"
    ]
    model.FinalDemandMeta = pd.merge(
        pd.read_parquet(
            utility_functions.get_named_dataset(
                'useeio_py.data',
                f"{model.specs['BaseIOLevel']}_FinalDemandCodeName_{model.specs['BaseIOSchema']}.parquet"
            )
            ##FIX: importlib.resources.files('useeio_py.data').joinpath(
            #    f"{model.specs['BaseIOLevel']}_FinalDemandCodeName_{model.specs['BaseIOSchema']}.parquet"
            #)
        ),
        utility_functions.stack(io_codes, merge_code_names),
        left_on=f"BEA_{model.specs['BaseIOSchema']}_{model.specs['BaseIOLevel']}_FinalDemand_Code",
        right_on="Code"
    )
    model.FinalDemandMeta = model.FinalDemandMeta.drop(columns = 'Code')
    
    if model.specs["IODataSource"] == "BEA":
        model.InternationalTradeAdjustmentMeta = utility_functions.stack(io_codes, ["InternationalTradeAdjustmentCodes"])
    model.MarginSectors = utility_functions.stack(io_codes, ["TransportationCodes", "WholesaleCodes", "RetailCodes"])
    model.ValueAddedMeta = pd.read_parquet(
        utility_functions.get_named_dataset(
            'useeio_py.data',
            f"{model.specs['BaseIOLevel']}_ValueAddedCodeName_{model.specs['BaseIOSchema']}.parquet"
        )
    )
    model_meta = list(filter(
        lambda x: x not in model_base_elements,
        model.get_elements()
    ))
    for meta in model_meta:
        # Change column names
        meta_val = getattr(model, meta)
        if meta == "Commodities":
            setattr(model, meta,
                getattr(model, meta).rename(
                    columns = {getattr(model, meta).columns[0]:"Code"}
                )
            )
        else:
            ncol = getattr(model, meta).shape[1]
            getattr(model, meta).columns = ["Code", "Name", "Group"][0:ncol]
        # Create a code_loc table
        loc = f"{model.specs['ModelRegionAcronyms'][0]}/"
        getattr(model, meta)['Code_Loc'] = loc + getattr(model, meta)['Code'].astype(str)
    model.Commodities["Unit"] = "USD"
    model.Industries["Unit"] = "USD"
    model.FinalDemandMeta["Group"] = model.FinalDemandMeta["Group"].str.replace(
        "Codes|DemandCodes", "", regex = True
    )
    model.MarginSectors["Name"] = model.MarginSectors["Name"].str.replace(
        "Codes", "", regex = True
    )

#DONE
def load_io_codes(model):
	'''Load BEA IO codes in a list based on model config'''
	io_codes = {}
	# Get IO sector codes by group
	io_codes["Commodities"] = utility_functions.get_vector_of_codes(
		model.specs['BaseIOSchema'],
		model.specs['BaseIOLevel'],
		"Commodity"
		)
	io_codes["Industries"] = utility_functions.get_vector_of_codes(
		model.specs['BaseIOSchema'],
		model.specs['BaseIOLevel'],
		"Industry"
		)

	codes = ["ValueAdded", "HouseholdDemand", "InvestmentDemand",
			"ChangeInventories", "Export", "Import", "GovernmentDemand",
			"Scrap", "Transportation", "Wholesale", "Retail"]
	
	for code in codes:
		io_codes[f"{code}Codes"] = utility_functions.get_vector_of_codes(
			model.specs['BaseIOSchema'],
			model.specs['BaseIOLevel'],
			code
		)
	
	fd_codes = ["HouseholdDemandCodes", "InvestmentDemandCodes",
				"ChangeInventoriesCodes", "ExportCodes",
				"ImportCodes", "GovernmentDemandCodes"]

	io_codes["FinalDemandCodes"] = []

	for code in fd_codes:
		io_codes["FinalDemandCodes"] += list(io_codes[code]["Code"])
	
	io_codes["FinalDemandCodes"] = pd.DataFrame(io_codes["FinalDemandCodes"], columns=["Code"])
	io_codes["InternationalTradeAdjustmentCodes"] = io_codes["ImportCodes"]["Code"].str.replace("F050", "F051")
	
	return(io_codes)

#DONE
def load_national_io_data(model, io_codes):
    '''Prepare economic components of an EEIO form USEEIO model.'''

    # Load BEA IO and gross output tables
    bea = load_bea_tables(model.specs, io_codes)

    # Generate domestic Use transaction and final demand
    domestic_use = io_functions.generate_domestic_use(pd.concat([bea["UseTransactions"], bea["FinalDemand"]], axis=1), model)
    bea['DomesticUseTransactions'] = domestic_use[io_codes['Industries']['Code']]
    bea['DomesticFinalDemand'] = domestic_use[io_codes['FinalDemandCodes']['Code']]

    # Generate Import Cost vector
    bea['InternationalTradeAdjustment'] = io_functions.generate_international_trade_adjustment_vector(
        pd.concat([bea["UseTransactions"], bea["FinalDemand"]], axis=1),
        model
    )
    # Modify row and column names to Code_Loc format in all IO tables
    # Use model.Industries
    code_loc_ind = model.Industries['Code_Loc']
    bea['MakeTransactions'] = bea['MakeTransactions'].set_index(code_loc_ind)
    bea['UseTransactions'].columns = code_loc_ind
    bea['DomesticUseTransactions'].columns = code_loc_ind
    bea['UseValueAdded'].columns = code_loc_ind
    
    # Use model.Commodities
    code_loc_com = model.Commodities['Code_Loc']
    bea['MakeTransactions'].columns = code_loc_com
    bea['UseTransactions'] = bea['UseTransactions'].set_index(code_loc_com)
    bea['DomesticUseTransactions'] = bea['DomesticUseTransactions'].set_index(code_loc_com)
    bea['FinalDemand'] = bea['FinalDemand'].set_index(code_loc_com)
    bea['DomesticFinalDemand'] = bea['DomesticFinalDemand'].set_index(code_loc_com)
    bea['InternationalTradeAdjustment'] = bea['InternationalTradeAdjustment'].set_index(code_loc_com)
    
    # Use model$FinalDemandMeta
    code_loc_fdm = model.FinalDemandMeta['Code_Loc']
    bea['FinalDemand'].columns = code_loc_fdm
    bea['DomesticFinalDemand'].columns = code_loc_fdm

     # Use model$ValueAddedMeta
    code_loc_vam = model.ValueAddedMeta['Code_Loc']
    bea['UseValueAdded'] = bea['UseValueAdded'].set_index(code_loc_vam)

    return(bea)

#DONE
def load_bea_tables(specs, io_codes):
    '''
    #' Load BEA IO tables in a list based on model config and io_codes.
    #' @param specs Model specifications.
    #' @param io_codes A list of BEA IO codes.
    #' @return A list with BEA IO tables
    '''
    bea = {}

    if specs['BasewithRedefinitions']:
        redef = "AfterRedef"
    else:
        redef = "BeforeRedef"
    
    bea["Make"] = pd.read_parquet(
        importlib.resources.files('useeio_py.data2').joinpath(
            f"{specs['BaseIOLevel']}_Make_{specs['IOYear']}_{redef}.parquet"
        )
    ).set_index('index')

    bea["Use"] = pd.read_parquet(
        importlib.resources.files('useeio_py.data2').joinpath(
            f"{specs['BaseIOLevel']}_Use_{specs['IOYear']}_{specs['BasePriceType']}_{redef}.parquet"
        )
    ).set_index('index')

     # Separate Make and Use tables into specific IO tables (all values in $)
    bea["MakeTransactions"] = bea["Make"].loc[
        io_codes['Industries']['Code'],
        io_codes['Commodities']['Code']
    ] * 1E6

    bea["MakeIndustryOutput"] = bea["MakeTransactions"].sum(axis=1)

    bea["UseTransactions"] = bea["Use"].loc[
        io_codes['Commodities']['Code'],
        io_codes['Industries']['Code']
    ] * 1E6
    
    bea["FinalDemand"] = bea["Use"].loc[
        io_codes['Commodities']['Code'],
        io_codes['FinalDemandCodes']['Code']
    ] * 1E6

    bea["UseValueAdded"] = bea["Use"].loc[
        io_codes['ValueAddedCodes']['Code'],
        io_codes['Industries']['Code']
    ] * 1E6

    bea["UseCommodityOutput"] = pd.concat(
        [bea['UseTransactions'], bea["FinalDemand"]],
        axis=1
    ).sum(axis=1)

    # Replace NA with 0 in IO tables
    if specs["BaseIOSchema"] == 2007:
        bea["MakeTransactions"] = bea["MakeTransactions"].fillna(0)
        bea["UseTransactions"] = bea["UseTransactions"].fillna(0)
        bea["FinalDemand"] = bea["FinalDemand"].fillna(0)

    return(bea)

#TODO: Test implementation
def load_two_region_state_io_tables(model):
    '''
    #' Load two-region state IO tables in a list based on model config.
    #' @param model An EEIO form USEEIO model object with model specs and IO meta data loaded.
    #' @return A list with state IO tables.
    '''
    state_io = {}
    # Load IO tables from stateior
    state_io['MakeTransactions'] = stateior_functions.get_two_region_io_data(model, "Make")
    state_io['UseTransactions'] = stateior_functions.get_two_region_io_data(model, "UseTransactions")
    state_io['FinalDemand'] = stateior_functions.get_two_region_io_data(model, "FinalDemand")
    state_io['DomesticUseTransactions'] = stateior_functions.get_two_region_io_data(model, "DomesticUseTransactions")
    state_io['DomesticFinalDemand'] = stateior_functions.get_two_region_io_data(model, "DomesticFinalDemand")
    state_io['UseValueAdded'] = stateior_functions.get_two_region_io_data(model, "UseValueAdded")
    state_io['InternationalTradeAdjustment'] = stateior_functions.get_two_region_io_data(model, "InternationalTradeAdjustment")
    return(state_io)

#TODO: Test implementation
def load_commodity_and_industry_output(model):
    '''
    Prepare commodity and industry output of an EEIO form USEEIO model.
    
    Argument:
    model:  A model object with model specs and fundamental IO data loaded.

    return: None
    '''
    if model.specs["IODataSource"] == "BEA":
        # Calculate industry and commodity output
        calculate_industry_commodity_output(model) #TODO
        # Load multi-year industry output
        model.MultiYearIndustryOutput = load_go_and_cpi.load_national_gross_output_table(model.specs)[model.Industries['Code']]
        model.MultiYearIndustryOutput = model.MultiYearIndustryOutput.set_index(model.Industries['Code_Loc'])
        model.MultiYearIndustryOutput[str(model.specs['IOYear'])] = model.IndustryOutput.copy()
        # Transform multi-year industry output to commodity output
        #TODO: Check this implementation. R Code used a [, FALSE] selection to eliminate all columns here. 
        # Not sure how this translates
        model.MultiYearCommodityOutput = model.CommodityOutput.copy()

        for year_col in model.MultiYearIndustryOutput.columns:
            model.MultiYearCommodityOutput[year_col] = io_functions.transform_industry_output_to_commodity_output_for_year(
                int(year_col),
                model
            )
        model.MultiYearCommodityOutput[str(model.specs['IOYear'])] = model.CommodityOutput.copy()
    elif model.specs['IODataSource'] == 'stateior':
        # Define state, year and iolevel
        if "US-DC" not in model.specs['ModelRegionAcronyms']:
            state_abb = re.sub(".*-", "", model.specs['ModelRegionAcronyms'][0])
            state = utility_functions.get_state_name_from_abb(state_abb)
        else:
            state = "District of Columbia"
        # Load industry and commodity output
        model.IndustryOutput =  stateior_functions.get_two_region_io_data(model, "IndustryOutput")
        model.CommodityOutput = stateior_functions.get_two_region_io_data(model, "CommodityOutput")
        # Load multi-year industry and commodity output
        years = range(2012, 2018)
        import copy
        tmp_model = copy.deepcopy(model)
        model.MultiYearIndustryOutput = model.IndustryOutput #[, FALSE]
        model.MultiYearCommodityOutput = model.CommodityOutput #[, FALSE]

        for year in years:
            tmp_model.specs['IOYear'] = year
            model.MultiYearIndustryOutput[str(year)] = stateior_functions.get_two_region_io_data(tmp_model, "IndustryOutput")
            model.MultiYearCommodityOutput[str(year)] = stateior_functions.get_two_region_io_data(tmp_model, "CommodityOutput")

#TODO: Test implementation
def calculate_industry_commodity_output(model):
    '''
    Calculate industry and commodity output vectors from model components.
    
    Argument:
    model:  An EEIO model object with model specs and IO tables loaded
    
    return: None
    '''
    model.IndustryOutput = model.UseTransactions.sum(axis=0) + model.UseValueAdded.sum(axis=0)
    model.CommodityOutput = model.UseTransactions.sum(axis=1) + model.FinalDemand.sum(axis=1)
