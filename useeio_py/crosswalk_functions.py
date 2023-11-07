# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from os import path
import requests

'''
Functions that use sector crosswalks
'''

def load_master_crosswalk():
    '''
    Function to externalize the BEA to NAICS crosswalk

    return: A crosswalk linking 2007 and 2012 NAICS codes to 2012 Sector, Summary, and Detail BEA codes
    '''
    bea_to_naics_crosswalk = master_crosswalk_2012
    return(bea_to_naics_crosswalk)

def get_naics_to_bea_allocation(year, model):
    '''
    #' Determine allocation factors between NAICS and BEA sectors based on Industry output.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param year Year of model Industry output.
    #' @return A table of allocation factors between NAICS and BEA sectors.
    '''
    logging.debug("Function not implemented")
    sys.exit()

#TODO: ensure file names are properly referenced in file structure for python module
#TODO: throw error if user inputs year other than 2012 or 2007
def get_naics_2_to_6_digits_code_name(year):
    '''
    Get 2-6 digit NAICS codes and names for year specified.

    Keyword argument:
    year:   int, 2012 or 2007 accepted

    return: dataframe with columns NAICS_year_Code and NAICS_year_Name.
    '''
    if year == 2012:
        file_name = "inst/extdata/2-digit_2012_Codes.xls"
        url = "https://www.census.gov/eos/www/naics/2012NAICS/2-digit_2012_Codes.xls"
    else:
        file_name = "inst/extdata/naics07.xls"
        url = "https://www.census.gov/eos/www/naics/reference_files_tools/2007/naics07.xls"
    
    if not path.exists(file_name):
        response = requests.get(url)
        with open(file_name, 'wb') as f:
            f.write(response.content)
    
    # Load 2-6 digits NAICS table. drop first row and first column
    naics = pd.read_excel(file_name, sheet_name = 1, header = 0).iloc[1:, 1:]
    naics.columns = ['naics_code', 'naics_name']

     # Split the NAICS code with dash ("-")
    dash_split = naics.assign(naics_code = naics.naics_code.str.split('-'))
    '''
    DashSplit = do.call("rbind.data.frame", apply(do.call("rbind", strsplit(NAICS$NAICS_Code, "-")),1, function(x) seq(x[1], x[2], 1)))
    colnames(DashSplit) <- c(paste("V", 1:ncol(DashSplit), sep=""))
    # Merge back with NAICS
    NAICSCodeName <- cbind(NAICS, DashSplit)
    # Reshape to long table
    NAICSCodeName <- reshape2::melt(NAICSCodeName[, -1], id.vars = "NAICS_Name")
    # Drop unwanted column and duplicated rows
    NAICSCodeName$variable <- NULL
    NAICSCodeName$value <- as.integer(NAICSCodeName$value)
    NAICSCodeName <- unique(NAICSCodeName)
    # Re-order and rename columns
    NAICSCodeName <- NAICSCodeName[, c("value", "NAICS_Name")]
    colnames(NAICSCodeName) <- paste("NAICS", year, c("Code", "Name"), sep = "_")
    return(NAICSCodeName)
    '''

def get_naics_2_to_6_digits(year):
    '''
    #' Get 2-6 digit NAICS codes in a crosswalk format for year specified.
    #' @param year int, 2012 or 2007 accepted.
    #' @return data frame with columns NAICS_2, NAICS_3, NAICS_4, NAICS_5, NAICS_6.
    '''
    if year == 2012:
        file_name = "inst/extdata/2-digit_2012_Codes.xls"
        url = "https://www.census.gov/eos/www/naics/2012NAICS/2-digit_2012_Codes.xls"
    else:
        file_name = "inst/extdata/naics07.xls"
        url = "https://www.census.gov/eos/www/naics/reference_files_tools/2007/naics07.xls"
    
    if not path.exists(file_name):
        response = requests.get(url)
        with open(file_name, 'wb') as f:
            f.write(response.content)
    '''
        
    # Load 2-6 digits NAICS table
    NAICS <- as.data.frame(readxl::read_excel(FileName, sheet = 1, col_names = TRUE))[-1,-1]
    colnames(NAICS) <- c("NAICS_Code", "NAICS_Name")
    NAICS$NAICS_Code <- suppressWarnings(as.integer(NAICS$NAICS_Code))
    NAICS <- NAICS[!is.na(NAICS$NAICS_Code), ]
    # Reshape the table
    NAICSwide <- as.data.frame(NAICS[nchar(NAICS$NAICS_Code)==6, ])
    NAICSwide[, paste0("NAICS_", c(2:5))] <- cbind(substr(NAICSwide$NAICS_Code, 1, 2),
                                                    substr(NAICSwide$NAICS_Code, 1, 3),
                                                    substr(NAICSwide$NAICS_Code, 1, 4),
                                                    substr(NAICSwide$NAICS_Code, 1, 5))
    NAICSwide$NAICS_6 <- NAICSwide$NAICS_Code
    NAICSwide <- NAICSwide[, -c(1:2)]
    return(NAICSwide)
'''

def get_naics_7_to_10_digits_code_name(year):
    '''
    #' Get 7-10 digit NAICS codes and names (agricultural, manufacturing, and mining industries) for year specified.
    #' @param year int. 2012 or 2007 accepted.
    #' @return data frame with columns NAICS_year_Code and NAICS_year_Name.
    '''
    logging.debug("Function not implemented")
    sys.exit()
    '''
    if (year==2012) {
        # Download Census 2012 Numerical List of Manufactured and Mineral Products
        SectorList <- c(211, 212, 213,
                        311, 312, 313, 314, 315, 316,
                        321, 322, 323, 324, 325, 326, 327,
                        331, 332, 333, 334, 335, 336, 337, 339)
        CensusNAICS <- data.frame()
        for(sector in SectorList) {
        FileName <- paste0("inst/extdata/CensusManufacturing2012NAICS_", sector, ".xls")
        url <- paste0("https://www.census.gov/manufacturing/numerical_list/", sector, ".xls")
        if(!file.exists(FileName)) {
            utils::download.file(url, FileName, mode = "wb")
        }
        CensusNAICS_sector <- as.data.frame(readxl::read_excel(FileName, sheet = 1,
                                                                col_names = TRUE, skip = 2))[, 1:2]
        colnames(CensusNAICS_sector) <- c("NAICS_2012_Code", "NAICS_2012_Name")
        CensusNAICS <- rbind(CensusNAICS, CensusNAICS_sector)
        }
        # NAICS from USDA
        coaNAICS <- utils::read.table(system.file("extdata", "Crosswalk_COAtoNAICS.csv", package = "useeior"),
                                    sep = ",", header = TRUE, stringsAsFactors = FALSE, check.names = FALSE)
        # Subset dataset and change column names to match other NAICS datasets
        coaNAICS <- coaNAICS[, c("NAICS_2012_Code", "Activity")]
        colnames(coaNAICS) <- c("NAICS_2012_Code", "NAICS_2012_Name")
        # Create 10 digit NAICS out of the 8 digit so Code name isn't dropped in future function
        coaNAICS10 <- coaNAICS
        coaNAICS10$NAICS_2012_Code <- stringr::str_pad(coaNAICS10$NAICS_2012_Code, width=10, side="right", pad="0")
        # row bind 8 digit and 10 digit Census of Ag NAICS
        coaNAICS <- rbind(coaNAICS, coaNAICS10)
        # row bind NAICS data from different sources
        CensusNAICS <- rbind(CensusNAICS, coaNAICS)
    }
    return(CensusNAICS)
'''

def get_naics_7_to_10_digits(year):
    '''
    #' Get 7-10 digit NAICS codes in a crosswalk format for year specified.
    #' @param year int. 2012 or 2007 accepted.
    #' @return data frame with columns NAICS_7, NAICS_8, NAICS_9, NAICS_10.
    '''
    logging.debug("Function not implemented")
    sys.exit()
    '''
    NAICSCodeName <- getNAICS7to10DigitsCodeName(year)
    # Change column name from year-specific to generic
    colnames(NAICSCodeName) <- c("NAICS_Code", "NAICS_Name")
    # Reshape the table
    NAICSwide <- as.data.frame(NAICSCodeName[nchar(NAICSCodeName$NAICS_Code)==10, ])
    NAICSwide[, paste0("NAICS_", c(7:9))] <- cbind(substr(NAICSwide$NAICS_Code, 1, 7),
                                                    substr(NAICSwide$NAICS_Code, 1, 8),
                                                    substr(NAICSwide$NAICS_Code, 1, 9))
    NAICSwide$NAICS_10 <- NAICSwide$NAICS_Code
    NAICSwide <- NAICSwide[, -c(1:2)]
    return(NAICSwide)
    '''

def get_naics_crosswalk(year):
    '''
    #' Get 2012 2-10 digit NAICS codes in a crosswalk format for year specified.
    #' @param year int. 2012 or 2007 accepted.
    #' @return data frame with columns NAICS_2, NAICS_3, NAICS_4, NAICS_5, NAICS_6, NAICS_7, NAICS_8, NAICS_9, NAICS_10.
    '''
    logging.debug("Function not implemented")
    sys.exit()
    '''
    # 2-6 digit
    NAICS_2to6 <- getNAICS2to6Digits(year)
    # 7-10 digit
    NAICS_7to10 <- getNAICS7to10Digits(year)
    NAICS_7to10$NAICS_6 <- substr(NAICS_7to10$NAICS_7, 1, 6)
    # Combine
    NAICS_2to10 <- merge(NAICS_2to6, NAICS_7to10, by = "NAICS_6", all.x = TRUE)
    # Re-order columns
    NAICS_2to10 <- NAICS_2to10[, paste("NAICS", c(2:10), sep = "_")]
    return(NAICS_2to10)
    '''

def get_naics_code_name(year):
    '''
    #' Get 2012 2-10 digit NAICS codes in a crosswalk format.
    #' @param year int. 2012 or 2007 accepted.
    #' @return data frame with columns NAICS_2, NAICS_3, NAICS_4, NAICS_5, NAICS_6,
    #' NAICS_7, NAICS_8, NAICS_9, NAICS_10.
    '''
    logging.debug("Function not implemented")
    sys.exit()
    '''
    # 2-6 digit
    NAICSCodeName_2to6 <- getNAICS2to6DigitsCodeName(year)
    # 7-10 digit
    NAICSCodeName_7to10 <- getNAICS7to10DigitsCodeName(year)
    # Combine
    NAICSCodeName_2to10 <- rbind.data.frame(NAICSCodeName_2to6, NAICSCodeName_7to10)
    return(NAICSCodeName_2to10)
    '''

def get_naics_2012_to_2007_concordances():
    '''
    #' Get 2012 NAICS to 2007 NAICS concordances at 6-digit level.
    #' @return data frame with columns '2012 NAICS Code', '2012 NAICS Title',
    #' '2007 NAICS Code', and '2007 NAICS Title'.
    '''
    file_name = "inst/extdata/2012_to_2017_NAICS.xlsx"
    url = "https://www.census.gov/naics/concordances/2012_to_2017_NAICS.xlsx"
    
    if not path.exists(file_name):
        response = requests.get(url)
        with open(file_name, 'wb') as f:
            f.write(response.content)
    '''
    df <- as.data.frame(readxl::read_excel(filename, sheet = 1, col_names = TRUE, skip = 2))
    df <- df[, startsWith(colnames(df), "20")]
    return(df)
    '''

def get_naics_2012_to_2017_concordances():
    '''
    #' Get 2012 NAICS to 2017 NAICS concordances at 6-digit level.
    #' @return data frame with columns '2012 NAICS Code', '2012 NAICS Title',
    #' '2017 NAICS Code', and '2017 NAICS Title'.
    '''
    file_name = "inst/extdata/2012_to_2017_NAICS.xlsx"
    url = "https://www.census.gov/naics/concordances/2012_to_2017_NAICS.xlsx"
    
    if not path.exists(file_name):
        response = requests.get(url)
        with open(file_name, 'wb') as f:
            f.write(response.content)
    '''
    df <- as.data.frame(readxl::read_excel(filename, sheet = 1, col_names = TRUE, skip = 2))
    df <- df[, startsWith(colnames(df), "20")]
    return(df)
    '''
