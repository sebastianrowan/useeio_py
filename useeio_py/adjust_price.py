# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


def adjust_result_matrix_price(matrix_name, currency_year, model, purchaser_price=True):
    '''
    #' Adjust price year and type (producer's or purchaser's) of a model result matrix.
    #' Model result matrices are M, M_d, N, N_d
    #' Year adjustments from 2007-2018 supported
    #' @param matrix_name Name of the result matrix that needs price adjustment, e.g. "N"
    #' @param currency_year An integer representing the currency year, e.g. 2018.
    #' @param purchaser_price A logical value indicating whether to adjust producer's price to purchaser's price.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @return A model result matrix after price adjustment
    #' @export
    '''
    logging.debug("Function not implemented")
    sys.exit()

def calculate_model_io_year_by_year_price_ratio(model):
    '''
    #' Calculate model IO year by year price ratio.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @return A dataframe of model IO year by year price ratio.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def calculate_producer_by_purchaser_price_ratio(model):
    '''
    #' Calculate producer to purchaser price ratio.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @return A dataframe of producer to purchaser price ratio.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def adjust_multiplier_price_year(matrix_name, currency_year, model):
    '''
    #' Adjust multipliers from IO year to currency year price.
    #' @param matrix_name Name of matrix representing the multiplier that needs price year adjustment.
    #' @param currency_year An integer representing the currency year.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @return A matrix representing the multiplier that is adjusted to currency year price.
    '''
    logging.debug("Function not implemented")
    sys.exit()

def adjust_multiplier_price_type(matrix, currency_year, model):
    '''
    #' Adjust multipliers from producer to purchaser price.
    #' @param matrix A matrix representing the multiplier that needs price type adjustment.
    #' @param currency_year An integer representing the currency year.
    #' @param model A complete EEIO model: a list with USEEIO model components and attributes.
    #' @return A matrix representing the multiplier that is adjusted to purchaser price.
    '''
    logging.debug("Function not implemented")
    sys.exit()