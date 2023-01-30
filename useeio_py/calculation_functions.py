# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype
from demand_functions import is_demand_vector_valid, format_demand_vector

def calculate_EEIO_model(model, perspective, demand = "Production", use_domestic_requirements = False):
    '''
    Calculate total emissions/resources (LCI) and total impacts (LCIA) for an EEIO model
    for a given perspective and demand vector.
    
    Arguments:
    model:          A complete EEIO Model: an instance of class Model as defined in useeio_classes.py
    perspective:    Perspective of the model: can be "DIRECT", "FINAL", or "BOTH". (useeior docs say can be "INTERMEDIATE", but function does not handle this option).
    demand:         A demand vector: can be a string specifying the name of a built-in demand vector, e.g. "Production",
                    or an actual demand vector with names as one or more model sectors and
                    numeric values in USD with the same dollar year as model.
    use_domestic_requirements:  
                    A logical value: if True, use domestic demand and L_d matrix; 
                    if False, use complete demand and L matrix.
    
    return: A dictionary with LCI and LCIA results (in data.frame format) of the EEIO model.
    '''
    
    result = {}
    # Generate Total Requirements (L or L_d) matrix based on whether "use_domestic"
    if use_domestic_requirements:
        L = model.L_d
    else:
        L = model.L
        
    # Prepare demand vector
    if type(demand) == str:
        # assume this is a model built-in demand
        # try to load the model vector
        if demand in model.demand_vectors['meta']['type']:
            if use_domestic_requirements:
                demand_name = f"2012_US_{demand}_Domestic"
            else:
                demand_name = f"2012_US_{demand}_Complete"
                
            # Get vector name (ID) from the meta table
            # *** I modified the above if-else block to bypass an additional lookup here
            d = model.demand_vectors['vectors'][demand_name]
        else:
            print(f"{demand} is not a valid demand vector name in model.")
    else:
        # Assume this is a user-defined demand vector
        #! Need to check that the given demand vector is valid
        if is_demand_vector_valid(demand, L):
            d = format_demand_vector(demand,L)
        else:
            print("Format of the demand vector is invalid. Cannot calculate result.")
    
    # Convert demand vector into a matrix
    # R: f <- as.matrix(d)
    f = d
    
    # Calculate LCI and LCIA in direct or final perspective
    if perspective == "DIRECT":
        # Calculate Direct Perspective LCI (a matrix with direct impacts in form of sector x flows)
        # print("Calculating Direct Perspective LCI...")
        s = get_scaling_vector(L, f) 
        result['LCI_d'] = calculate_direct_perspective_LCI(model.B, s)
        # print("Calculating Direct Perspective LCIA...")
        result['LCIA_d'] = calculate_direct_perspective_LCIA(model.D, s)
    elif perspective == "FINAL":
        # print("Calculating Final Perspective LCI...")
        result['LCI_f'] = calculate_final_perspective_LCI(model.M, f) 
        # print("Calculating Final Perspective LCIA...")
        result['LCIA_f'] = calculate_final_perspective_LCIA(model.N, f) 
    elif perspective == "BOTH":
        # Calculate Direct Perspective LCI (a matrix with direct impacts in form of sector x flows)
        # print("Calculating Direct Perspective LCI...")
        s = get_scaling_vector(L, f)
        result['LCI_d'] = calculate_direct_perspective_LCI(model.B, s)
        # Calculate Direct Perspective LCIA (matrix with direct impacts in form of sector x impacts)
        # print("Calculating Direct Perspective LCIA...")
        result['LCIA_d'] = calculate_direct_perspective_LCIA(model.D, s)
        
        # Calculate Final Perspective LCI (a matrix with total impacts in form of sector x flows)
        # print("Calculating Final Perspective LCI...")
        result['LCI_f'] = calculate_final_perspective_LCI(model.M, f)
        # Calculate Final Perspective LCIA (matrix with total impacts in form of sector x impacts)
        # print("Calculating Final Perspective LCIA...")
        result['LCIA_f'] = calculate_final_perspective_LCIA(model.N, f)
    else:
        print(f"{perspective} is not a valid perspective in the model.")
    
    # print("Result calculation complete.")
    return(result)


def get_scaling_vector(L, demand):
    '''
    Multiply the Leontief inverse L and the demand vector to calculate scaling vector
    that represents production needed to fulfill the demand.
    
    Arguments:
    L:      Leontief inverse.
    demand: Final demand vector
    
    return: Scaling vector
    
    references: Yang, Yi, Wesley W. Ingwersen, Troy R. Hawkins, Michael Srocka, and David E. Meyer.
                2017. “USEEIO: A New and Transparent United States Environmentally-Extended Input-Output Model.”
                Journal of Cleaner Production 158 (August): 308–18. https://doi.org/10.1016/j.jclepro.2017.04.150.
                SI1, Equation 8.
    '''
    s = np.matmul(L, np.asarray(demand))
    return(s)
        
def calculate_direct_perspective_LCI(B, s):
    '''
    The direct perspective LCI aligns flows with sectors consumed by direct use.
    Multiply the B matrix and the scaling vector s.
    
    Arguments:
    B:  Marginal impact per unit of the environmental flows.
    s:  Scaling vector.
    
    return: A matrix with direct impacts in form of sector x flows.
    
    references: Yang, Yi, Wesley W. Ingwersen, Troy R. Hawkins, Michael Srocka, and David E. Meyer.
                2017. “USEEIO: A New and Transparent United States Environmentally-Extended Input-Output Model.”
                Journal of Cleaner Production 158 (August): 308–18. https://doi.org/10.1016/j.jclepro.2017.04.150.
                SI1, Equation 9.
    '''
    lci_d = np.transpose(np.matmul(B, np.diag(s.iloc[:,0])))
    lci_d.index = s.index
    return(lci_d)
    
    
def calculate_final_perspective_LCI(M, y):
    '''
    The final perspective LCI aligns flows with sectors consumed by final users.
    Multiply the M matrix and the diagonal of demand, y.
    
    Arguments:
    M:  a model M matrix, direct + indirect flows per $ output of sector.
    y:  a model demand vector
    
    return: A matrix with total impacts in form of sectors x flows.
    
    references: Yang, Yi, Wesley W. Ingwersen, Troy R. Hawkins, Michael Srocka, and David E. Meyer.
                2017. “USEEIO: A New and Transparent United States Environmentally-Extended Input-Output Model.”
                Journal of Cleaner Production 158 (August): 308–18. https://doi.org/10.1016/j.jclepro.2017.04.150.
                SI1, Equation 10.
    '''
    ## print(f"demand vect for lci_f calc: {y}")
    lci_f = np.transpose(np.matmul(M, np.diag(y.iloc[:,0])))
    lci_f.index = M.columns
    
    return(lci_f)


def calculate_direct_perspective_LCIA(D, s):
    '''
    The direct perspective LCIA aligns impacts with sectors consumed by direct use.
    Multiply the D matrix (the product of C matrix and B matrix) and scaling vector s.
    
    Arguments:
    D:  a model D matrix, Direct impact per unit of the environmental flows.
    s:  Scaling vector.
    
    return: A matrix with direct impacts in form of sector x impact categories.
    
    references: Yang, Yi, Wesley W. Ingwersen, Troy R. Hawkins, Michael Srocka, and David E. Meyer.
                2017. “USEEIO: A New and Transparent United States Environmentally-Extended Input-Output Model.”
                Journal of Cleaner Production 158 (August): 308–18. https://doi.org/10.1016/j.jclepro.2017.04.150.
                SI1, Equation 9.
    '''
    lcia_d = np.transpose(np.matmul(D, np.diag(s.iloc[:,0])))
    lcia_d.index = s.index
    return(lcia_d)
    
    
def calculate_final_perspective_LCIA(N, y):
    '''
    The final perspective LCIA aligns impacts with sectors consumed by final users.
    Multiply the N matrix and the diagonal of demand, y.
    
    Arguments:
    N: a model N matrix, direct + indirect impact per unit of the environmental flows.
    y:  a model demand vector
    
    return: A matrix with total impacts in form of sector x impact categories.
    
    references: Yang, Yi, Wesley W. Ingwersen, Troy R. Hawkins, Michael Srocka, and David E. Meyer.
                2017. “USEEIO: A New and Transparent United States Environmentally-Extended Input-Output Model.”
                Journal of Cleaner Production 158 (August): 308–18. https://doi.org/10.1016/j.jclepro.2017.04.150.
                SI1, Equation 10.
    '''
    lcia_f = np.transpose(np.matmul(N, np.diag(y.iloc[:,0])))
    lcia_f.index = N.columns
    return(lcia_f)
  

def calculate_sector_contribution_to_impact(model, sector, indicator, domestic=False):
    '''
    #' Calculate the percent contribution of sectors to direct+indirect impacts by an indicator,
    #' using the product of model L matrix (total requirements) and D matrix (direct impacts by indicator).
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param sector, str, index of a model sector for use in the L matrix, e.g. "221100/US".
    #' @param indicator, str, index of a model indicator for use in the D matrix, e.g. "Acidification Potential".
    #' @param domestic, boolean, sets model to use domestic flow matrix. Default is FALSE.
    #' @return A dataframe sorted by contribution (high-to-low), also showing "L", "D", "impact".
    #' @export
    '''
    pass

def calculate_flow_contribution_to_impact(model, sector, indicator, domestic=False):
    '''
    #' Calculate the percent contribution of flows to direct+indirect impacts by an indicator,
    #' using model M matrix for total impacts of flows and C matrix for indicator.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @param sector, str, index of a model sector for use in the M matrix, e.g. "221100/US".
    #' @param indicator, str, index of a model indicator for use in the C matrix, e.g. "Acidification Potential".
    #' @param domestic, boolean, sets model to use domestic flow matrix. Default is FALSE.
    #' @return A dataframe sorted by contribution (high-to-low), also showing "M", "C", "impact".
    #' @export 
    '''
    pass

def aggregate_result_matrix_by_row(matrix, to_level, crosswalk):
    '''
    #' Aggregate result matrix by rows
    #'
    #' @param matrix      A matrix with sectors as rows
    #' @param to_level    The level of BEA code this matrix will be aggregated to
    #' @param crosswalk   Sector crosswalk between levels of detail
    #' @return An aggregated matrix with sectors as rows
    #' @export
    '''
    pass

def aggregate_result_matrix(matrix, to_level, crosswalk):
    '''
    #' Aggregate result matrix by rows and columns
    #'
    #' @param matrix      A matrix with sectors as rows and columns
    #' @param to_level    The level of BEA code this matrix will be aggregated to
    #' @param crosswalk   Sector crosswalk between levels of detail
    #' @return An aggregated matrix with sectors as rows and columns
    #' @export
    '''
    pass

def calculate_sector_purchased_by_sector_sourced_impact(y, model, indicator):
    '''
    #' Calculates sector x sector impacts from a given demand vector.
    #' @param y a model demand vector or user-specified demand vector
    #' that must have the same dimension with the model demand vector
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes
    #' @param indicator str, index of a model indicator, e.g. "Acidification Potential"
    #' @return A matrix of impacts in the form of sector purchased x sector sourced,
    #' negative values should be interpreted as "reduced impacts".
    #' @export
    '''
    pass

def calculate_margin_sector_impacts(model):
    '''
    #' Calculate sector margin impacts in the form of M and N Matrix
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @return A list with M_margin and N_margin
    #' @export
    '''
    pass

def disaggregate_total_to_direct_and_tier1(model, indicator):
    '''
    #' For a given indicator, disaggregate total impacts per purchase (N) into 
    #' direct impacts (D) and upstream, Tier 1 purchase impacts. Return a long format
    #' dataframe of exchanges, with sector names mapped to sector codes.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes
    #' @param indicator str, index of a model indicator, e.g. "Greenhouse Gases".
    #' @export
    #' @return A data frame of direct and per-tier-1-purchase sector impacts
    '''
    pass

def calculate_total_impact_by_tier1_purchase(model, indicator):
    '''
    #' Calculate sector x sector total impacts (single indicator) for Tier 1 purchases
    #' Multiply each row of sector x sector A matrix by scalar elements of an
    #' indicator (single) x sector array from N
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes
    #' @param indicator str, index of a model indicator, e.g. "Greenhouse Gases".
    #' @return A sector x sector, impact-per-tier-1-purchase matrix.
    '''
    pass


