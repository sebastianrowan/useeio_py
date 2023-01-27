# -*- coding: utf-8 -*-

import pkgutil
import importlib.resources
import os.path
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
import re
from .configuration_functions import get_configuration
from .utility_functions import get_vector_of_codes


class Model:
    
    def __init__(self, model_name, config_paths = None):
        '''
        Initialize model with specifications and fundamental crosswalk table.

        Keyword arguments:
        modelname:      Name of the model from a config file.
        configpaths:    str list, paths (including file name) of model configuration file
                        and optional agg/disagg configuration file(s).
                        If None, built-in config files are used.
        '''
        print("begin model initialization...")
        self.valid = True
        self.invalid_reason = None
        # Get model specs
        self.specs = get_configuration(model_name, "model", config_paths)

        if self.specs is None:
            self.valid = False
            self.invalid_reason = f"No configuration exists for a model named {model_name}"
        else:
            # Get model crosswalk
            crosswalk_name = f"MasterCrosswalk{self.specs['BaseIOSchema']}.parquet"
            crosswalk_parquet = importlib.resources.files('useeio_py.data').joinpath(crosswalk_name)
            crosswalk = pd.read_parquet(crosswalk_parquet)
            cols = ["NAICS_2012_Code"] + list((crosswalk.filter(regex = "^BEA", axis=1).columns))
            crosswalk = crosswalk[cols]
            crosswalk = crosswalk.drop_duplicates()
            crosswalk = crosswalk.rename(
                columns = lambda x: re.sub(
                    f"_{self.specs['BaseIOSchema']}|_Code",
                    "", x))
            # Assign initial model crosswalk based on base schema
            model_schema = "USEEIO"
            base_schema = f"BEA_{self.specs['BaseIOLevel']}"
            crosswalk[model_schema] = crosswalk[base_schema]
            self.crosswalk = crosswalk

    def load_io_data(self):
        '''
        Prepare economic components of an EEIO form USEEIO model
        '''
        # Declare model IO objects
        print("Initializing IO tables...")
        # Load model IO meta
        '''
        ## Declare model IO objects
        #logging::loginfo("Initializing IO tables...")
        # Load model IO meta
        model <- loadIOmeta(model)
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
    
    def load_io_meta(self):
        '''Prepare metadata of economic components of an EEIO form USEEIO model'''
        io_codes = self.load_io_codes()
        '''
        io_codes <- loadIOcodes(model$specs)
        model_base_elements <- names(model)
        model$Commodities <- merge(as.data.frame(io_codes$Commodities, stringsAsFactors = FALSE),
                                    utils::read.table(system.file("extdata", "USEEIO_Commodity_Meta.csv",
                                                                package = "useeior"),
                                                    sep = ",", header = TRUE, stringsAsFactors = FALSE),
                                    by.x = "io_codes$Commodities", by.y = "Code",
                                    all.x = TRUE, sort = FALSE)
        model$Industries <- get(paste(model$specs$BaseIOLevel, "IndustryCodeName",
                                        model$specs$BaseIOSchema, sep = "_"))
        model$FinalDemandMeta <- merge(get(paste(model$specs$BaseIOLevel, "FinalDemandCodeName",
                                                model$specs$BaseIOSchema, sep = "_")),
                                        utils::stack(io_codes[c("HouseholdDemandCodes",
                                                                "InvestmentDemandCodes",
                                                                "ChangeInventoriesCodes",
                                                                "ExportCodes", "ImportCodes",
                                                                "GovernmentDemandCodes")]),
                                        by = 1, sort = FALSE)
        if (model$specs$IODataSource=="BEA") {
            model$InternationalTradeAdjustmentMeta <- utils::stack(io_codes["InternationalTradeAdjustmentCodes"])
        }
        model$MarginSectors <- utils::stack(io_codes[c("TransportationCodes",
                                                        "WholesaleCodes", "RetailCodes")])
        model$ValueAddedMeta <- get(paste(model$specs$BaseIOLevel, "ValueAddedCodeName",
                                            model$specs$BaseIOSchema, sep = "_"))
        model_meta <- names(model)[!names(model) %in% model_base_elements]
        # Format model IO meta and add Code_Loc column
        for (meta in model_meta) {
            # Change column names
            if (meta=="Commodities") {
            colnames(model[[meta]])[1] <- "Code"
            } else {
            colnames(model[[meta]]) <- c("Code", "Name", "Group")[1:ncol(model[[meta]])]
            }
            # Create a code_loc table
            code_loc <- cbind(model[[meta]][["Code"]], rep(model$specs$ModelRegionAcronyms,
                                                        each = length(model[[meta]][["Code"]])))
            # Repeat model IO meta df to prepare for adding Code_Loc
            model[[meta]] <- as.data.frame(lapply(model[[meta]], rep,
                                                nrow(code_loc)/nrow(model[[meta]])))
            model[[meta]][] <- lapply(model[[meta]], as.character)
            # Add Code_Loc column
            model[[meta]][["Code_Loc"]] <- apply(code_loc, 1, FUN = joinStringswithSlashes)
        } 
        model$Commodities$Unit <- "USD"
        model$Industries$Unit <- "USD"
        # Apply final touches to FinalDemandMeta and MarginSectors
        model$FinalDemandMeta$Group <- gsub(c("Codes|DemandCodes"), "",
                                            model$FinalDemandMeta$Group)
        model$MarginSectors$Name <- gsub(c("Codes"), "", model$MarginSectors$Name)
        return(model)
        '''

    def load_io_codes(self):
        '''Load BEA IO codes in a list based on model config'''
        io_codes = {}
        # Get IO sector codes by group
        io_codes["Commodities"] = get_vector_of_codes(
            self.specs['BaseIOSchema'],
            self.specs['BaseIOLevel'],
            "Commodity"
            )
        io_codes["Industries"] = get_vector_of_codes(
            self.specs['BaseIOSchema'],
            self.specs['BaseIOLevel'],
            "Industry"
            )

        codes = ["ValueAdded", "HouseholdDemand", "InvestmentDemand",
                "ChangeInventories", "Export", "Import", "GovernmentDemand",
                "Scrap", "Transportation", "Wholesale", "Retail"]
        
        for code in codes:
            io_codes[f"{code}Codes"] = get_vector_of_codes(
                self.specs['BaseIOSchema'],
                self.specs['BaseIOLevel'],
                code
            )
        
        fd_codes = ["HouseholdDemandCodes", "InvestmentDemandCodes",
                    "ChangeInventoriesCodes", "ExportCodes",
                    "ImportCodes", "GovernmentDemandCodes"]

        io_codes["FinalDemandCodes"] = []

        for code in fd_codes:
            io_codes["FinalDemandCodes"] += list(io_codes[code])
        
        io_codes["FinalDemandCodes"] = pd.DataFrame(io_codes["FinalDemandCodes"])
        io_codes["InternationalTradeAdjustmentCodes"] = io_codes["ImportCodes"]["Code"].str.replace("F050", "F051")
        
        return(io_codes)