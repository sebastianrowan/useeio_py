# -*- coding: utf-8 -*-
'''Functions to load margins data'''

import logging
import pandas as pd
import numpy as np
import importlib.resources
from . import utility_functions, io_functions

#TODO: test implementation
def get_margins_table(model):
    '''
    Generate Margins table using BEA Margin Details table which include all industries and final demand.
    
    Argument
    model:  A complete EEIO model with USEEIO model components and attributes.

    return: A data.frame containing CommodityCode, and margins for ProducersValue, Transportation, Wholesale, Retail and PurchasersValue.
    '''
    # Define value_columns in Margins table
    value_columns = ["ProducersValue", "Transportation", "Wholesale", "Retail"]
    # Use BEA Margin Details table
    if model.specs['BaseIOSchema'] == 2012:
        margins_table = pd.read_parquet(
            importlib.resources.files('useeio_py.data2').joinpath(
                'Detail_Margins_2012_BeforeRedef.parquet'
            )
        )
        margins_table[value_columns] *= 1E6
    else:
        logging.debug("This case is not handles in the R code. What to do?")
    # Remove Export, Import and Change in Inventory records.
    # Exports do not reflect what a US consumer would pay for margins, hence the removal.
    # Imports have negative PRO price which impacts calculations. 
    # Change in inventory has negative margins for positive change, which does not accurately portray actual margins either.
    pr_list = ["Export", "Import", "ChangeInventories"]
    purchaser_removal = [utility_functions.get_vector_of_codes(io_schema=model.specs['BaseIOSchema'], io_level='Detail', col_name=i) for i in pr_list]
    
    margins_table = margins_table.query('NIPACode not in @purchaser_removal') # keep rows if their NIPA code is not in the purchaser_removal list
    
    #TODO: ensure this query works properly. If it doesn't, rows will not be removed

    # Remove Scrap, Used and secondhand goods, and Non-comparable imports, and Rest of world adjustment commodities
    cr_list = ["Scrap", "UsedGoods", "NonComparableImport", "RowAdjustment"] #RoWAdjustment in R code
    commodity_removal = [utility_functions.get_vector_of_codes(io_schema=model.specs['BaseIOSchema'], io_level=model.specs['BaseIOLevel'], col_name=i) for i in cr_list]
    margins_table = margins_table.query('NIPACode not in @purchaser_removal') # keep rows if their NIPA code is not in the commodity_removal list
    
    #TODO: ensure this query works properly. If it doesn't, rows will not be removed

    # Convert negative PRO values to non-negative
    # This addresses remaining negative PRO values for cases like subsidies
    margins_table['ProducersValue'] = abs(margins_table['ProducersValue'])

    # Map to Summary and Sector level
    crosswalk_cols = [col for col in model.crosswalk if col.startswith("BEA")]
    crosswalk = model.crosswalk[crosswalk_cols].drop_duplicates()
    margins_table = margins_table.merge(crosswalk, how='left', left_on="CommodityCode", right_on="BEA_Detail")
    # Aggregate value_columns by CommodityCode (dynamic to model BaseIOLevel) and CommodityDescription
    if model.specs['BaseIOLevel'] != "Detail":
        margins_table["CommodityCode"] = margins_table[f"BEA_{model.specs['BaseIOLevel']}"]
    margins_table = margins_table.groupby("CommodityCode")[value_columns].agg('sum')
    commodity_code = list(margins_table.index)
    margins_table = margins_table.reset_index()
    # logging.debug(margins_table)
    # Keep model Commodities
    margins_table = margins_table.merge(model.Commodities[["Code","Name", "Code_Loc"]], how='right', left_on="CommodityCode", right_on="Code")
    margins_table = margins_table.fillna(0)
    margins_table = margins_table.query('Code_Loc in @model.Commodities["Code_Loc"]') # R code: MarginsTable <- MarginsTable[match(model$Commodities$Code_Loc, MarginsTable$Code_Loc), ]
    #TODO: does this work? the R code will only return the first matching row. If there is more than one row per Code_Loc, this won't work.

    # Transform MarginsTable from Commodity to Industry format
    if model.specs['CommodityorIndustryType'] != "Industry":
        # Generate a commodity x industry commodity mix matrix, see Miller and Blair section 5.3.2
        commodity_mix = io_functions.generate_commodity_mix_matrix(model) #TODO
        #Create a margins table for industries based on model industries
        margins_table_industry = model.Industries[["Code"]]
        margins_table_industry.columns=['IndustryCode']

        # Transform PRO value and Margins for Commodities from Commodity to Industry format, (Margins' * C_m )'
        margins_values_com = margins_table[value_columns]
        margins_values_ind = np.transpose(np.matmul(np.transpose(margins_values_com.to_numpy()), commodity_mix)) 
        # Merge Industry Margins Table with Commodity Margins Table to add in metadata columns

        margins_table_industry.loc[:,value_columns] = margins_values_ind
        cols = [col for col in margins_table if col not in value_columns]
        margins_table = pd.merge(margins_table_industry, margins_table[cols], how='left', left_on='IndustryCode', right_on='CommodityCode')
        margins_table = margins_table.fillna(0)
    
    # Calculate Purchaser's value
    margins_table['PurchasersValue'] = margins_table[["ProducersValue", "Transportation", "Wholesale", "Retail"]].sum(axis=1)
    # Rename code column from CommodityCode/IndustryCode to SectorCode
    colnames = list(margins_table.columns)
    colnames[0] = "SectorCode"
    margins_table.columns = colnames
    return(margins_table)

