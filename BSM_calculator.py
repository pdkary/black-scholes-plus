import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime
from scipy.stats import norm
import re

def get_time_to_expiry(maturity):
    # Today's date
    day_0 = datetime.today()
    # Maturity date
    date_format = "%Y-%m-%d"
    day_exp = datetime.strptime(maturity, date_format)
    # Delta date: i.e. 1 day, 0:00:00
    date_to_exp = day_exp - day_0
    # Delta days: i.e. 1 day
    days_to_exp = date_to_exp.days
    return days_to_exp

def get_annualization_factor(interval):
    hours_per_day = 8
    days_per_year = 252
    if interval=='1m':
        return days_per_year*hours_per_day*60
    elif interval=='2m':
        return days_per_year*hours_per_day*30
    elif interval=='5m':
        return days_per_year*hours_per_day*12
    elif interval=='30m':
        return days_per_year*hours_per_day*2
    elif interval=='60m':
        return days_per_year*hours_per_day
    elif interval=='90m':
        return days_per_year*hours_per_day*2/3
    elif interval=='1h':
        return days_per_year*hours_per_day
    elif interval=='1d':
        return days_per_year
    elif interval=='5d':
        return days_per_year/5
    elif interval=='1wk':
        return days_per_year/7
    elif interval=='1mo':
        return 12
    elif interval=='3mo':
        return 4

class BSM_Calculator:
    def __init__(self, tickers, period='1mo', interval='1h'):
        self.tickers = tickers
        self.period = period
        self.interval = interval
        self.ticker_data = self.load_data()

    def load_data(self):
        tkr_str = " ".join(self.tickers)
        spot_data = yf.download(tickers=tkr_str,
                                period=self.period,
                                interval=self.interval,
                                group_by='ticker')
        # fix multi-column errors
        spot_data.columns = spot_data.columns.map("_".join)
        return spot_data

    def load_option_data(self, expiration_date,strike_map):
        first_digit_regex = r'(^[^\d]+)'
        option_chains = {t: yf.Ticker(t).option_chain(expiration_date) for t in self.tickers}
        option_df = pd.DataFrame()

        for t in self.tickers:
            call_chain = option_chains[t].calls
            call_row = call_chain.loc[call_chain['strike']==strike_map[t]]
            call_row = call_row[['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility']]
            call_row['contractSymbol'] = call_row['contractSymbol'].apply(lambda x: x[0:x.index('2')])
            call_row['type'] = ['CALL' for i in range(len(call_row['bid']))]

            put_chain = option_chains[t].puts
            put_row = put_chain.loc[put_chain['strike']==strike_map[t]]
            put_row = put_row[['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility']]
            put_row['contractSymbol'] = put_row['contractSymbol'].apply(lambda x: x[0:x.index('2')])
            put_row['type'] = ['PUT' for i in range(len(put_row['bid']))]

            if not call_row.empty:
                option_df = option_df.append(call_row)
            if not put_row.empty:
                option_df = option_df.append(put_row)
        
        option_df = option_df.reset_index(drop=True)
        cols = option_df.columns.tolist()
        cols = [cols[0],cols[-1]] + cols[1:-1]
        return option_df[cols]
        
    def refresh(self):
        self.ticker_data = self.load_data()

    def get_spot_price(self):
        close_strs = [x+"_Close" for x in self.tickers]
        spot_price = self.ticker_data.tail(1)[close_strs].iloc[0]
        spot_price.index = spot_price.index.map(
            lambda x: x.replace("_Close", ""))
        return round(spot_price, 4)

    def get_standard_deviation(self):
        # # Get closing price
        close_strs = [x+"_Close" for x in self.tickers]
        data_close = self.ticker_data[close_strs]

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

    def bsm_calculation(self, strike_map, exp_date, rfr, div_yield):
        time_to_exp = get_time_to_expiry(exp_date)/365
        spot = self.get_spot_price()
        vol = self.get_standard_deviation()
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
        option_df = self.load_option_data(expiration_date,strike_map)
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

if __name__ == '__main__':
    tickers = ['IYZ', 'AAPL', 'AMD', 'AMGN', 'AMZN', 'BCE', 'CSCO', 'FB','GOOG', 'IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP', 'VZ']
    strike_map = {'IYZ':50,'AAPL':200,'AMD':120,'AMGN':400,'AMZN':3600,'BCE':60,'CSCO':60,'FB':300,'GOOG':2200,'IBM':150,'INTC':70,'MSFT':300,'MU':100,'NFLX':600,'NVDA':650,'SHOP':1750,'VZ':75}

    expiration_date = "2021-03-19"
    bsmc = BSM_Calculator(tickers,interval='1h')
    bsmc_data = bsmc.get_report(expiration_date,strike_map,0.012,0)

    print("-"*56+ "BSMC DATA"+"-"*56)
    print(bsmc_data)
    print("-"*(56*2+9))
