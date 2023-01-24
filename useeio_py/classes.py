# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

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
    
    def __init__(
        self, model_name, config_paths
    ):
        pass