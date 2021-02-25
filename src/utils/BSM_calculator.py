import pandas as pd
import yfinance as yf
import numpy as np
from scipy.stats import norm
from src.utils.time_helpers import *
from src.data.spot_data_service import SpotDataService
from src.data.option_data_service import OptionDataService


class BSM_Calculator:
    """
    tkrs:       (1xN) array of ticker indicies
    strikes:    (1xN) corresponding strike prices
    vol:        (1xN) corresponding annual volitility
    rfr:        (scalar) risk free rate
    div_yield:  (scalar) divident yield
    expr_dates: (Nx?) matrix of tkr: (1x?) array of expiration dates
    """
    @staticmethod
    def bsm_calculation(tkrs,spot,strike,vol,rfr,div_yield,expr_dates):
        bsm_data = pd.DataFrame(dtype=object)
        for i in range(len(expr_dates.index)):
            expr_i = expr_dates.loc[expr_dates.index == i]
            data_i = BSM_Calculator.get_single_expiration(tkrs,spot,strike,vol,rfr,div_yield,expr_i)
            bsm_data = bsm_data.append(data_i)
        return bsm_data.loc[bsm_data["expiration"] != 0].reset_index(drop=True)

    """
    spots:      (1xN) spot prices (tkr:spot)
    strike:     (1xN) spot prices (tkr:strike)
    vol:        (1xN) volatility  (tkr:vol)
    rfr:        (1x1) risk free yield
    div_yield   (1x1) div yield
    expr_date   (1xN) expr_date   (tkr:expr)
    """
    @staticmethod
    def get_single_expiration(tkrs,spot,strike,vol,rfr,div_yield,expr_dates):
        t_to_expr = expr_dates.apply(np.vectorize(get_time_to_expiry))
        d1 = (np.log(spot/strike) + t_to_expr*(rfr-div_yield+vol*vol/2))/(vol*np.sqrt(t_to_expr))

        d2 = d1 - vol*np.sqrt(t_to_expr)

        N = lambda x: norm.cdf(x)
        Nprime = lambda x: norm.pdf(x)

        Kr = np.exp(-rfr*t_to_expr)
        Kq = np.exp(-div_yield*t_to_expr)
        
        CV = spot*Kq*N(d1)- strike*Kr*N(d2)
        PV = strike*Kr*N(-d2) - spot*Kq*N(-d1)
        Cdelta = Kq*N(d1)
        Pdelta = Kq*(N(d1)-1)
        rfr = np.array([rfr])
        div_yield = np.array([div_yield])

        Gamma  = Kq/(spot*vol*np.sqrt(t_to_expr))*Nprime(d1)

        T = 252
        Ctheta = (1/T)*(-(spot*vol*Kq*Nprime(d1)/(2*np.sqrt(t_to_expr))) - rfr*strike*Kr*N(d2) + div_yield*spot*Kq*N(d1))
        Ptheta = (1/T)*(-(spot*vol*Kq*Nprime(d1)/(2*np.sqrt(t_to_expr))) + rfr*strike*Kr*N(-d2)- div_yield*spot*Kq*N(-d1))

        factor = np.array([1.0/100.0])
        vega = factor*spot*Kq*np.sqrt(t_to_expr)*Nprime(d1)

        Crho = factor*strike*t_to_expr*Kr*N(d2)
        Prho = factor*strike*t_to_expr*Kr*N(-d2)
        
        bsm_data = pd.DataFrame()
        bsm_data["symbol"] = tkrs
        bsm_data["expiration"] = expr_dates[tkrs].values[0]
        bsm_data["Call Value"] = CV[tkrs].values[0]
        bsm_data["Put Value"] = PV[tkrs].values[0]
        bsm_data["Call Delta"] = Cdelta[tkrs].values[0]
        bsm_data["Put Delta"] = Pdelta[tkrs].values[0]
        bsm_data["Gamma"] = Gamma[tkrs].values[0]
        bsm_data["Call Theta"] = Ctheta[tkrs].values[0]
        bsm_data["Put Theta"] = Ptheta[tkrs].values[0]
        bsm_data["Vega"] = vega[tkrs].values[0]
        bsm_data["Call Rho"] = Crho[tkrs].values[0]
        bsm_data["Put Rho"] = Prho[tkrs].values[0]
        bsm_data["Annual Vol"] = vol.values
        return bsm_data
