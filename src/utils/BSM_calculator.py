import pandas as pd
import yfinance as yf
import numpy as np
from scipy.stats import norm
from src.utils.time_helpers import *
from src.data.spot_data_service import SpotDataService
from src.data.option_data_service import OptionDataService

class BSM_Calculator:
    """
    Now we will have multiple expr dates, and strike prices for earch tkr, so we will need additional rows in our dataframe
    """
    @staticmethod
    def bsm_calculation(tkrs,spot,strikes_map,vol,rfr,div_yield,exprs_map):
        bsm_data = pd.DataFrame(dtype=object)
        i = 0
        for tkr in tkrs:
            for s in strikes_map[tkr]:
                for expr in exprs_map[tkr]:
                    tmp = pd.DataFrame({"symbol":tkr,"spot":spot[tkr],"strike":s,"vol":vol[tkr],"rfr":rfr,"div_yield":div_yield,"expr_date":expr},index=[i])
                    bsm_data = bsm_data.append(tmp)
                    i+=1
        return BSM_Calculator.bsm_from_dataframe(bsm_data)

    """
    Here, each row has the following structure
    tkr|spot|strike|vol|rfr|div_yield|expr_date|   
    """
    @staticmethod
    def bsm_from_dataframe(df):
        tkrs = list(df['symbol'])
        spot = df['spot']
        strike = df['strike']
        vol = df['vol']
        rfr = df['rfr']
        div_yield = df['div_yield']
        expr_dates = df['expr_date']
        t_to_expr = expr_dates.apply(get_time_to_expiry)

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
        bsm_data["spot"] = spot.values
        bsm_data["strike"] = strike.values
        bsm_data["expiration"] = expr_dates.values
        bsm_data["Call Value"] = CV.values
        bsm_data["Put Value"] = PV.values
        bsm_data["Call Delta"] = Cdelta.values
        bsm_data["Put Delta"] = Pdelta.values
        bsm_data["Gamma"] = Gamma.values
        bsm_data["Call Theta"] = Ctheta.values
        bsm_data["Put Theta"] = Ptheta.values
        bsm_data["Vega"] = vega.values
        bsm_data["Call Rho"] = Crho.values
        bsm_data["Put Rho"] = Prho.values
        bsm_data["Annual Vol"] = vol.values
        return bsm_data
