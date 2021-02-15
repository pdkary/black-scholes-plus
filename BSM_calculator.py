import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime
from scipy.stats import norm


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
        option_chains = {t: yf.Ticker(t).option_chain(expiration_date) for t in self.tickers}
        call_df = pd.DataFrame(columns=['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility'])
        put_df = pd.DataFrame(columns=['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility'])
        for t in self.tickers:
            call_chain = option_chains[t].calls
            call_row = call_chain.loc[call_chain['strike']==strike_map[t]]
            call_row = call_row[['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility']]
            
            put_chain = option_chains[t].puts
            put_row = put_chain.loc[put_chain['strike']==strike_map[t]]
            put_row = put_row[['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility']]
            
            if not call_row.empty:
                call_df = call_df.append(call_row)
            if not put_row.empty:
                put_df = put_df.append(put_row)
        
        return call_df,put_df
        
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
        annual_std = standard_deviation * (252 ** 0.5)
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
        bsm_data["Strike Price"] = strike_map.values()
        bsm_data["Annual Volatility"] = vol[self.tickers]
        return(bsm_data.transpose())


if __name__ == '__main__':
    tickers = ['GOOG', 'AAPL', 'AMZN', 'IBM']
    strike_map = {'GOOG':1200,'AAPL':130,'AMZN':2000,'IBM':120}

    bsmc = BSM_Calculator(tickers)
    bsmc_data = bsmc.bsm_calculation(strike_map,'2021-03-14',0,0)
    call_df,put_df = bsmc.load_option_data('2021-03-05',strike_map)
    
    print("------------------------------------BSMC DATA------------------------------------")
    print(bsmc_data)
    print("-----------------------------------RECENT CALLS---------------------------------")
    print(call_df)
    print("-----------------------------------RECENT PUTS----------------------------------")
    print(put_df)
