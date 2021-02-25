import yfinance as yf
import pandas as pd
import numpy as np
from math import isnan
from datetime import datetime, timedelta

class MovingAverageService:
    def __init__(self,tkrs,period='6mo'):
        self.tickers = tkrs
        self.period = period
        self.interval = "1d"
        self.refresh_data()

    def log(self,var):
        with open("MAService.log","a+") as f:
            f.write(str(var))

    def load_data(self):
        tkr_str = " ".join(self.tickers)
        spot_data = yf.download(tickers=tkr_str,
                                period=self.period,
                                interval=self.interval,
                                group_by='ticker',
                                progress=False)
        # fix multi-column indicies
        if type(spot_data.columns) == pd.MultiIndex:
            spot_data.columns = spot_data.columns.map("_".join)
        
        return spot_data
    
    def get_moving_average(self):
        keys = [tkr+"_Close" for tkr in self.tickers]
        rolling_mean = self.data[keys].rolling(window=50).mean()
        rolling_mean = rolling_mean.loc[rolling_mean[keys[0]] > 0]
        max_rm = rolling_mean.max(axis=0)
        min_rm = rolling_mean.min(axis=0)
        df = pd.DataFrame(index=keys)
        df["Low MA"] = min_rm
        df["High MA"] = max_rm
        return df
    
    def refresh_data(self):
        self.data = self.load_data()
        self.MA = self.get_moving_average()
        self.avg_change = self.get_average_change_after_MA_hit(5)
    """
    This function will look over the past data, and analyze the average % change seen in a stock (looking behind and ahead)
    after the stock has hit its 50 day moving average.
    """
    def get_average_change_after_MA_hit(self,lookback_days=4):
        keys = [tkr+"_Close" for tkr in self.tickers]
        closes = self.data[keys]

        upper_ts = self.MA["High MA"]
        lower_ts = self.MA["Low MA"]
        hits = pd.DataFrame()
        for x in keys:
            hits[x] = closes[x].loc[(closes[x] < upper_ts[x]) & (closes[x] > lower_ts[x])]
        
        hit_dict = {tkr:[0,0] for tkr in keys}
        for d in hits.index[lookback_days+1:-(lookback_days+1)]:
            dd = d.strftime("%Y-%m-%d")
            ld = self.get_lookaround_difference(dd,lookback_days)
            for k in ld.index:
                if abs(hits.loc[dd][k]) > 0:
                    hit_dict[k][0]+=ld[k]
                    hit_dict[k][1]+=1
        
        hit_dict = {tkr.split("_")[0]:hit_dict[tkr][0]/hit_dict[tkr][1] for tkr in hit_dict.keys()}
        return hit_dict
    
    def get_lookaround_difference(self,date,days=4):
        keys = [tkr+"_Close" for tkr in self.tickers]
        center_date = datetime.strptime(date,"%Y-%m-%d")
        center_date_index = list(self.data.index).index(center_date)
        forward_days = self.data.index[center_date_index+days].strftime("%Y-%m-%d")
        backward_days = self.data.index[center_date_index-days].strftime("%Y-%m-%d")

        forward_vals = self.data.loc[forward_days]
        backward_vals = self.data.loc[backward_days]

        price_change = (forward_vals - backward_vals)/backward_vals
        return price_change[keys]
    
    def get_action(self,tkr,bid,ask,invested_cash,available_cash,tkr_vwap):
        returnStr = dict()
        if invested_cash > 0:
            if tkr_vwap > 0 and bid > tkr_vwap*(1+self.avg_change[tkr]/2):
                returnStr[tkr] = "cashsell/"+str(round(tkr_vwap*invested_cash))
        else:
            if self.is_within_MA(tkr,ask):
                if self.avg_change[tkr] > 0:
                    returnStr[tkr] = "cashbuy/"+str(round(self.avg_change[tkr]*available_cash))
        return returnStr
        
    def is_within_MA(self,tkr,val):
        tkr = tkr+"_Close"
        return self.MA["Low MA"][tkr] < val and self.MA["High MA"][tkr] > val
