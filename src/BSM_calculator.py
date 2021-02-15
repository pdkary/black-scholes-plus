import pandas as pd
import yfinance as yf
import numpy as np
from scipy.stats import norm
from src.time_helpers import *
from src.spot_data_service import SpotDataService
from src.option_data_service import OptionDataService


class BSM_Calculator:
    def __init__(self, tickers, period='3mo', interval='1d'):
        self.tickers = tickers
        self.period = period
        self.interval = interval
        self.spot_service = SpotDataService(tickers,period,interval)
        self.option_service = OptionDataService(tickers)

    def bsm_calculation(self, strike_map, exp_date, rfr, div_yield):
        time_to_exp = get_time_to_expiry(exp_date)/365
        spot = self.spot_service.get_latest()
        vol = self.spot_service.get_stdev()
        strike_ps = np.array(list(strike_map.values()))

        d1 = (np.log(spot / strike_ps) + ((rfr - div_yield) +
                                          vol*vol / 2.) * time_to_exp) / (vol * np.sqrt(time_to_exp))
        d2 = d1 - vol*np.sqrt(time_to_exp)

        K_exp = strike_ps*np.exp(rfr*time_to_exp)
        bsm_call_value = spot*norm.cdf(d1) - norm.cdf(d2)*K_exp
        bsm_put_value = K_exp - spot + bsm_call_value

        bsm_data = pd.DataFrame()
        bsm_data["Call value"] = bsm_call_value[self.tickers]
        bsm_data["Put value"] = bsm_put_value[self.tickers]
        bsm_data["Annual Volatility"] = vol[self.tickers]
        return bsm_data

    def get_report(self,expiration_date,strike_map,rfr,div_yield):
        option_df = self.option_service.get_data(expiration_date,strike_map)
        bsmc_data = self.bsm_calculation(strike_map,expiration_date,rfr,div_yield)

        symbols = option_df['contractSymbol']
        types = option_df['type']

        def get_val(symbol,type):
            if type=="CALL":
                return bsmc_data["Call value"][symbol]
            elif type=="PUT":
                return bsmc_data["Put value"][symbol]

        option_df["BSM Value"] = np.vectorize(get_val)(symbols,types).round(2)
        option_df["Annual Volatility"] = symbols.apply(lambda x: bsmc_data["Annual Volatility"][x])

        cols = option_df.columns.tolist()
        cols = cols[0:3] + cols[-2:-1] + cols[3:-2] + cols[-1:]

        return option_df[cols].round(4)
