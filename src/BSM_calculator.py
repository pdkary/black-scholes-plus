import pandas as pd
import yfinance as yf
import numpy as np
from scipy.stats import norm
from src.time_helpers import *
from src.spot_data_service import SpotDataService
from src.option_data_service import OptionDataService


class BSM_Calculator:
    @staticmethod
    def bsm_calculation(spot,vol,strike_map,expr_date,rfr,div_yield):
        time_to_exp = get_time_to_expiry(expr_date)/365
        strike_ps = np.array(list(strike_map.values()))

        d1 = (np.log(spot / strike_ps) + ((rfr - div_yield) +
                                          vol*vol / 2.) * time_to_exp) / (vol * np.sqrt(time_to_exp))
        d2 = d1 - vol*np.sqrt(time_to_exp)

        K_exp = strike_ps*np.exp(rfr*time_to_exp)
        bsm_call_value = spot*norm.cdf(d1) - norm.cdf(d2)*K_exp
        bsm_put_value = K_exp - spot + bsm_call_value

        tkrs = list(strike_map.keys())
        bsm_data = pd.DataFrame()
        bsm_data["Call value"] = bsm_call_value[tkrs]
        bsm_data["Put value"] = bsm_put_value[tkrs]
        bsm_data["Annual Vol"] = vol[tkrs]
        return bsm_data
