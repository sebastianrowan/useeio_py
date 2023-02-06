# -*- coding: utf-8 -*-
'''Functions for loading input-output tables'''

import logging
import importlib.resources
import pandas as pd
from . import utility_functions
from .io_functions import generate_domestic_use
import numpy as np

def load_io_data(model, config_paths = None):
    '''
    Prepare economic components of an EEIO form USEEIO model
    '''
    # Declare model IO objects
    logging.info("Initializing IO tables...")
    # Load model IO meta
    load_io_meta(model)
    io_table_names = [
        "MakeTransactions", "UseTransactions", "DomesticUseTransactions",
        "UseValueAdded", "FinalDemand", "DomesticFinalDemand",
        "InternationalTradeAdjustment"
    ]
    if model.specs['IODataSource'] == "BEA":
        io_codes = load_io_codes(model)
        #for name in io_table_names:
            #setattr(model, name, load_national_io_data(io_codes)[name]) #TODO: implement load_national_io_data
    '''
    ## Declare model IO objects
    #logging::loginfo("Initializing IO tables...")
    ## Load model IO meta
    #model <- loadIOmeta(model)
    # Define IO table names
    io_table_names <- c("MakeTransactions", "UseTransactions", "DomesticUseTransactions",
                        "UseValueAdded", "FinalDemand", "DomesticFinalDemand",
                        "InternationalTradeAdjustment")
    # Load IO data
    if (model$specs$IODataSource=="BEA") {
        io_codes <- loadIOcodes(model$specs)
        model[io_table_names] <- loadNationalIOData(model, io_codes)[io_table_names]
    } else if (model$specs$IODataSource=="stateior") {
        model[io_table_names] <- loadTwoRegionStateIOtables(model)[io_table_names]
    }
    
    # Add Industry and Commodity Output
    model <- loadCommodityandIndustryOutput(model)
    
    # Transform model FinalDemand and DomesticFinalDemand to by-industry form
    if (model$specs$CommodityorIndustryType=="Industry") {
        # Keep the orignal FinalDemand (in by-commodity form)
        model$FinalDemandbyCommodity <- model$FinalDemand
        model$DomesticFinalDemandbyCommodity <- model$DomesticFinalDemand
        model$InternationalTradeAdjustmentbyCommodity <- model$InternationalTradeAdjustment
        model$FinalDemand <- transformFinalDemandwithMarketShares(model$FinalDemand, model)
        model$DomesticFinalDemand <- transformFinalDemandwithMarketShares(model$DomesticFinalDemand, model)
        model$InternationalTradeAdjustment <- unlist(transformFinalDemandwithMarketShares(model$InternationalTradeAdjustment, model))
        names(model$InternationalTradeAdjustment) <- model$Industries$Code_Loc
    }
    
    # Add Margins table
    model$Margins <- getMarginsTable(model)
    
    # Add Chain Price Index (CPI) to model
    model$MultiYearIndustryCPI <- loadChainPriceIndexTable(model$specs)[model$Industries$Code, ]
    rownames(model$MultiYearIndustryCPI) <- model$Industries$Code_Loc
    # Transform industry CPI to commodity CPI
    model$MultiYearCommodityCPI <- as.data.frame(model$Commodities, row.names = model$Commodities$Code_Loc)[, FALSE]
    for (year_col in colnames(model$MultiYearIndustryCPI)) {
        model$MultiYearCommodityCPI[, year_col] <- transformIndustryCPItoCommodityCPIforYear(as.numeric(year_col), model)
    }
    
    # Check for aggregation
    if(!is.null(model$specs$AggregationSpecs)){
        model <- getAggregationSpecs(model, configpaths)
        model <- aggregateModel(model)
    }
    
    # Check for disaggregation
    if(!is.null(model$specs$DisaggregationSpecs)){
        model <- getDisaggregationSpecs(model, configpaths)
        model <- disaggregateModel(model)
    }
    
    # Check for hybridization
    if(model$specs$ModelType == "EEIO-IH"){
        model <- getHybridizationSpecs(model, configpaths)
        model <- getHybridizationFiles(model, configpaths)
    }
        
    return(model)
    '''

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

#TODO
def load_national_io_data(model, io_codes):
    '''Prepare economic components of an EEIO form USEEIO model.'''

    # Load BEA IO and gross output tables
    bea = load_bea_tables(model.specs, io_codes) #TODO

    # Generate domestic Use transaction and final demand
    domestic_use = generate_domestic_use(pd.merge(bea["UseTransactions"], bea["FinalDemand"], axis=1), model) #TODO
    
    
    '''
    # Load BEA IO and gross output tables
    #BEA <- loadBEAtables(model$specs, io_codes)
    ## Generate domestic Use transaction and final demand
    #DomesticUse <- generateDomesticUse(cbind(BEA$UseTransactions, BEA$FinalDemand), model)
    BEA$DomesticUseTransactions <- DomesticUse[, io_codes$Industries]
    BEA$DomesticFinalDemand <- DomesticUse[, io_codes$FinalDemandCodes]
    # Generate Import Cost vector
    BEA$InternationalTradeAdjustment <- generateInternationalTradeAdjustmentVector(cbind(BEA$UseTransactions, BEA$FinalDemand), model)
    # Modify row and column names to Code_Loc format in all IO tables
    # Use model$Industries
    rownames(BEA$MakeTransactions) <- colnames(BEA$UseTransactions) <-
        colnames(BEA$DomesticUseTransactions) <- colnames(BEA$UseValueAdded) <-
        model$Industries$Code_Loc
    # Use model$Commodities
    colnames(BEA$MakeTransactions) <- rownames(BEA$UseTransactions) <-
        rownames(BEA$DomesticUseTransactions) <- rownames(BEA$FinalDemand) <-
        rownames(BEA$DomesticFinalDemand) <- names(BEA$InternationalTradeAdjustment) <-
        model$Commodities$Code_Loc
    # Use model$FinalDemandMeta
    colnames(BEA$FinalDemand) <- colnames(BEA$DomesticFinalDemand) <-
        model$FinalDemandMeta$Code_Loc
    # Use model$ValueAddedMeta
    rownames(BEA$UseValueAdded) <- model$ValueAddedMeta$Code_Loc
    return(BEA)
    '''

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
   

def load_two_region_state_io_tables(model):
    '''
    #' Load two-region state IO tables in a list based on model config.
    #' @param model An EEIO form USEEIO model object with model specs and IO meta data loaded.
    #' @return A list with state IO tables.
    '''
    pass
    '''
    StateIO <- list()
    # Load IO tables from stateior
    StateIO$MakeTransactions <- getTwoRegionIOData(model, "Make")
    StateIO$UseTransactions <- getTwoRegionIOData(model, "UseTransactions")
    StateIO$FinalDemand <- getTwoRegionIOData(model, "FinalDemand")
    StateIO$DomesticUseTransactions <- getTwoRegionIOData(model, "DomesticUseTransactions")
    StateIO$DomesticFinalDemand <- getTwoRegionIOData(model, "DomesticFinalDemand")
    StateIO$UseValueAdded <- getTwoRegionIOData(model, "ValueAdded")
    StateIO$InternationalTradeAdjustment <- getTwoRegionIOData(model, "InternationalTradeAdjustment")
    return(StateIO)
    '''

def load_commodity_and_industry_output(model):
    '''
    #' Prepare commodity and industry output of an EEIO form USEEIO model.
    #' @param model A model object with model specs and fundamental IO data loaded.
    #' @return A list with USEEIO model economic components.
    '''
    pass
    '''
    if (model$specs$IODataSource=="BEA") {
        # Calculate industry and commodity output
        model <- calculateIndustryCommodityOutput(model)
        # Load multi-year industry output
        model$MultiYearIndustryOutput <- loadNationalGrossOutputTable(model$specs)[model$Industries$Code, ]
        rownames(model$MultiYearIndustryOutput) <- model$Industries$Code_Loc
        model$MultiYearIndustryOutput[, as.character(model$specs$IOYear)] <- model$IndustryOutput
        # Transform multi-year industry output to commodity output
        model$MultiYearCommodityOutput <- as.data.frame(model$CommodityOutput)[, FALSE]
        for (year_col in colnames(model$MultiYearIndustryOutput)) {
        model$MultiYearCommodityOutput[, year_col] <- transformIndustryOutputtoCommodityOutputforYear(as.numeric(year_col), model)
        }
        model$MultiYearCommodityOutput[, as.character(model$specs$IOYear)] <- model$CommodityOutput
    } else if (model$specs$IODataSource=="stateior") {
        # Define state, year and iolevel
        if (!"US-DC"%in%model$specs$ModelRegionAcronyms) {
        state <- state.name[state.abb==gsub(".*-", "", model$specs$ModelRegionAcronyms[1])]
        } else {
        state <- "District of Columbia"
        }
        # Load industry and commodity output
        model$IndustryOutput <- getTwoRegionIOData(model, "IndustryOutput")
        model$CommodityOutput <- getTwoRegionIOData(model, "CommodityOutput")
        # Load multi-year industry and commodity output
        years <- as.character(2012:2017)
        tmpmodel <- model
        model$MultiYearIndustryOutput <- as.data.frame(model$IndustryOutput)[, FALSE]
        model$MultiYearCommodityOutput <- as.data.frame(model$CommodityOutput)[, FALSE]
        for (year in years) {
        tmpmodel$specs$IOYear <- year
        model$MultiYearIndustryOutput[, year] <- getTwoRegionIOData(tmpmodel, "IndustryOutput")
        model$MultiYearCommodityOutput[, year] <- getTwoRegionIOData(tmpmodel, "CommodityOutput")
        }
    }
    return(model)
    '''

def calculate_industry_commodity_output(model):
    '''
    #' Calculate industry and commodity output vectors from model components.
    #' @param model An EEIO model object with model specs and IO tables loaded
    #' @return An EEIO model with industry and commodity output added
    '''
    pass
    '''
    model$IndustryOutput <- colSums(model$UseTransactions) + colSums(model$UseValueAdded)
    model$CommodityOutput <- rowSums(model$UseTransactions) + rowSums(model$FinalDemand)
    return(model)
    '''
