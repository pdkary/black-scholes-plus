import yfinance as yf
import numpy as np
from src.time_helpers import *

class SpotDataService:
    def __init__(self,tickers,period,interval):
        self.tickers = tickers
        self.period = period
        self.interval = interval
        self.data = self.load_data()
    
    def load_data(self):
        tkr_str = " ".join(self.tickers)
        spot_data = yf.download(tickers=tkr_str,
                                period=self.period,
                                interval=self.interval,
                                group_by='ticker')
        # fix multi-column errors
        spot_data.columns = spot_data.columns.map("_".join)
        return spot_data
    
    def get_latest(self):
        close_strs = [x+"_Close" for x in self.tickers]
        spot_price = self.data.tail(1)[close_strs].iloc[0]
        spot_price.index = spot_price.index.map(
            lambda x: x.replace("_Close", ""))
        return round(spot_price, 4)
    
    def get_stdev(self):
        # # Get closing price
        close_strs = [x+"_Close" for x in self.tickers]
        data_close = self.data[close_strs]

        # # Get % change ( day_1 / day_0 ) - 1
        per_change = (data_close / data_close.shift(1)) - 1
        # # Delete first datum (NaN)
        per_change = per_change.iloc[1:]
        # # Standard deviation
        standard_deviation = np.std(per_change)

        # # Annualized standard dev
        annual_std = standard_deviation * np.sqrt(get_annualization_factor(self.interval))
        annual_std.index = annual_std.index.map(
            lambda x: x.replace("_Close", ""))
        return annual_std