# -*- coding: utf-8 -*-

import pkgutil
import os.path
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from configuration_functions import get_configuration

class Model:
    
    def __init__(
        self, crosswalk, commodities, industries, final_demand_meta, international_trade_adjustment_meta,
        margin_sectors, value_added_meta, multi_year_industry_output, multi_year_commodity_output,
        margins, multi_year_industry_cpi, multi_year_commodity_cpi, satellite_tables, indicators, demand_vectors,
        TbS, CbS, V, C_m, V_n, U, U_d, q, x, mu, A, A_d, L, L_d, B, C, D, M, M_d, N, N_d, Rho, Phi
    ):
        self.crosswalk = crosswalk
        self.commodities = commodities
        self.industries = industries
        self.final_demand_meta = final_demand_meta
        self.international_trade_adjustment_meta = international_trade_adjustment_meta
        self.margin_sectors = margin_sectors
        self.value_added_meta = value_added_meta
        self.multi_year_industry_output = multi_year_industry_output
        self.multi_year_commodity_output = multi_year_commodity_output
        self.margins = margins
        self.multi_year_industry_cpi = multi_year_industry_cpi
        self.multi_year_commodity_cpi = multi_year_commodity_cpi
        self.satellite_tables = satellite_tables
        self.indicators = indicators
        self.demand_vectors = demand_vectors
        self.TbS = TbS
        self.CbS = CbS
        self.V = V
        self.C_m = C_m
        self.V_n = V_n
        self.U = U
        self.U_d = U_d
        self.q = q
        self.x = x
        self.mu = mu
        self.A = A
        self.A_d = A_d
        self.L = L
        self.L_d = L_d
        self.B = B
        self.C = C
        self.D = D
        self.M = M
        self.M_d = M_d
        self.N = N
        self.N_d = N_d
        self.Rho = Rho
        self.Phi = Phi

class Model2:
    
    def __init__(self, model_name, config_paths):
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
        self.specs = get_configuration(model_name, "model", config_paths)

        if self.specs is None:
            self.valid = False
            self.invalid_reason = f"No configuration exists for a model named {model_name}"
        else:
            crosswalk_name = f"MasterCrosswalk{self.specs['BaseIOSchema']}.parquet"
            crosswalk_path = f"data/{crosswalk_name}"
            crosswalk = pd.read_parquet(pkgutil.get_data(__name__, crosswalk_path))

        '''
        #startLogging()
        #logging::loginfo("Beginmodel initialization...")
        #model <- list()
        ## Get model specs
        #model$specs <- getConfiguration(modelname, "model", configpaths)
        #if (rlang::is_na(model$specs)) {
        #    stop(paste("No configuration exists for a model named", modelname))
        #} else {
            ## Get model crosswalk
            #crosswalk <- get(paste0("MasterCrosswalk", model$specs$BaseIOSchema),
            #                as.environment("package:useeior"))
            crosswalk <- unique(crosswalk[, c("NAICS_2012_Code",
                                            colnames(crosswalk)[startsWith(colnames(crosswalk), "BEA")])])
            colnames(crosswalk) <- gsub(paste0("_", model$specs$BaseIOSchema, "|_Code"),
                                        "", colnames(crosswalk))
            rownames(crosswalk) <- NULL
            # Assign initial model crosswalk based on base schema
            modelschema <- "USEEIO"
            baseschema <- paste0("BEA_", model$specs$BaseIOLevel)
            crosswalk[modelschema] <- crosswalk[baseschema]
            model$crosswalk <- crosswalk
        }
        return(model)
        '''