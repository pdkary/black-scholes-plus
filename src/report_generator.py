from src.spot_data_service import SpotDataService
from src.option_data_service import OptionDataService
from src.BSM_calculator import BSM_Calculator
from src.time_helpers import get_time_to_expiry
import numpy as np
import pandas as pd
from math import ceil,nan

class ReportGenerator:
    display_cols = ['contractSymbol','expiration','type','spot','strike','BSM Value','BSM% over ask', 'lastPrice', 'bid', 'ask', 'B/E','d% for BE','openInterest','Delta','Gamma','Theta','Vega','Rho','impliedVolatility', 'Annual Vol']

    def __init__(self, tickers,rfr):
        self.tickers = tickers
        self.rfr = rfr
        self.spot_service = SpotDataService(tickers)
        self.option_service = OptionDataService(tickers)

    def get_ATM_report(self,expiration_date):
        return self.get_ATM_plus_x(expiration_date,0)

    def get_ATM_plus_x(self,expiration_date,x):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]+x,0) for t in self.tickers}
        return self.get_report(expiration_date,s_map)

    def get_ATM_plus_x_percent(self,expiration_date,x):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]*(1+x),0) for t in self.tickers}
        return self.get_report(expiration_date,s_map)

    def get_ATM_multi_report(self,endDate=None):
        return self.get_ATM_multi_report_plus_x(0,endDate)

    def get_ATM_multi_report_plus_x(self,x,endDate=None):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]+x,0) for t in self.tickers}
        return self.get_multi_expiration_report(s_map,endDate)

    def get_ATM_multi_report_plus_x_percent(self,x,endDate=None):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]*(1+x),0) for t in self.tickers}
        return self.get_multi_expiration_report(s_map,endDate)
    
    def get_multi_expiration_report(self,strike_map,endDate=None):
        spots = self.spot_service.get_latest()

        expr_dates = self.option_service.get_expiration_dates(endDate)
        
        option_df = self.option_service.get_all_expiration_data(strike_map)
        if option_df.empty:
            return option_df
        option_df = option_df.reset_index(drop=True)
        
        strikes = [strike_map[x] for x in self.tickers]
        vol = self.spot_service.get_stdev()
        bsmc_data = BSM_Calculator.bsm_calculation(self.tickers,spots,strikes,vol,0.012,0,expr_dates)

        idxs = option_df.index
        symbols = option_df['contractSymbol'].apply(lambda x:x[0:x.index("2")])
        types = option_df['type']
        exprs = option_df['expiration']
        strikes = option_df['strike']
        
        put_BE = strikes - option_df["ask"]
        call_BE = strikes + option_df["ask"]

        ## functions in need of vectorization
        def bsmc_get(symbol,expr,type,val_call,vall_put):
            if type == "CALL":
                return bsmc_data.loc[((bsmc_data['expiration']==expr) & (bsmc_data['symbol']==symbol)),val_call]
            elif type == "PUT":
                return bsmc_data.loc[((bsmc_data['expiration']==expr) & (bsmc_data['symbol']==symbol)),vall_put]

        def get_breakeven(idx,type):
            if type=="PUT":
                return put_BE[idx]
            elif type=="CALL":
                return call_BE[idx]
        
        def get_percent_over(val1,val2):
            if val2==0:
                return nan
            val = (val1-val2)/val2
            val_sign = val/abs(val)
            return val_sign*round(abs(val),2)

        vector_bsmc_get = np.vectorize(bsmc_get)
        option_df["BSM Value"] = vector_bsmc_get(symbols,exprs,types,'Call Value','Put Value').round(2)
        option_df["Annual Vol"] = vector_bsmc_get(symbols,exprs,types,'Annual Vol','Annual Vol')
        option_df["Delta"] = vector_bsmc_get(symbols,exprs,types,'Call Delta','Put Delta')
        option_df["Gamma"] = vector_bsmc_get(symbols,exprs,types,'Gamma','Gamma')
        option_df["Theta"] = vector_bsmc_get(symbols,exprs,types,'Call Theta','Put Theta')
        option_df["Vega"] = vector_bsmc_get(symbols,exprs,types,'Vega','Vega')
        option_df["Rho"] = vector_bsmc_get(symbols,exprs,types,"Call Rho","Put Rho")
        option_df["B/E"] = np.vectorize(get_breakeven)(idxs,types)

        option_df["spot"] = symbols.apply(lambda x: spots[x])
        option_df['d% for BE'] = round((option_df['B/E'] - option_df['spot'])/option_df['spot'],2)
        option_df['BSM% over ask'] = np.vectorize(get_percent_over)(option_df['BSM Value'],option_df['ask'])
        return option_df[self.display_cols]
    
    def get_report(self, expiration_date, strike_map):
        spots = self.spot_service.get_latest()
        option_df = self.option_service.get_data(expiration_date, strike_map)
        if option_df.empty:
            return option_df
        strikes = np.array([strike_map[x] for x in self.tickers])
        expr_dates = pd.Series([expiration_date]*len(self.tickers),index=self.tickers)
        
        bsmc_data = BSM_Calculator.get_single_expiration(
            tkrs=self.tickers,
            spot=spots, 
            vol=self.spot_service.get_stdev(), 
            strike=strikes, 
            expr_dates=expr_dates, 
            rfr=self.rfr,
            div_yield=0)

        idxs = option_df.index
        
        symbols = option_df['contractSymbol'].apply(lambda x:x[0:x.index("2")])
        types = option_df['type']
        exprs = option_df['expiration']
        strikes = option_df['strike']
        
        put_BE = strikes - option_df["ask"]
        call_BE = strikes + option_df["ask"]

        ## functions in need of vectorization
        def bsmc_get(symbol,expr,type,val_call,vall_put):
            if type == "CALL":
                return bsmc_data.loc[((bsmc_data['expiration']==expr) & (bsmc_data['symbol']==symbol)),val_call]
            elif type == "PUT":
                return bsmc_data.loc[((bsmc_data['expiration']==expr) & (bsmc_data['symbol']==symbol)),vall_put]

        def get_breakeven(idx,type):
            if type=="PUT":
                return put_BE[idx]
            elif type=="CALL":
                return call_BE[idx]
        
        def get_percent_over(val1,val2):
            val = (val1-val2)/val2
            val_sign = val/abs(val)
            return val_sign*round(abs(val),2)

        vector_bsmc_get = np.vectorize(bsmc_get)
        option_df["BSM Value"] = vector_bsmc_get(symbols,exprs,types,'Call Value','Put Value').round(2)
        option_df["Annual Vol"] = vector_bsmc_get(symbols,exprs,types,'Annual Vol','Annual Vol')
        option_df["Delta"] = vector_bsmc_get(symbols,exprs,types,'Call Delta','Put Delta')
        option_df["Gamma"] = vector_bsmc_get(symbols,exprs,types,'Gamma','Gamma')
        option_df["Theta"] = vector_bsmc_get(symbols,exprs,types,'Call Theta','Put Theta')
        option_df["Vega"] = vector_bsmc_get(symbols,exprs,types,'Vega','Vega')
        option_df["Rho"] = vector_bsmc_get(symbols,exprs,types,"Call Rho","Put Rho")
        option_df["B/E"] = np.vectorize(get_breakeven)(idxs,types)

        option_df["spot"] = symbols.apply(lambda x: spots[x])
        option_df['d% for BE'] = round((option_df['B/E'] - option_df['spot'])/option_df['spot'],2)
        option_df['BSM% over ask'] = np.vectorize(get_percent_over)(option_df['BSM Value'],option_df['ask'])
        return option_df[self.display_cols]