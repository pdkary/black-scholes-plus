from src.data.spot_data_service import SpotDataService
from src.data.option_data_service import OptionDataService
from src.utils.BSM_calculator import BSM_Calculator
from src.utils.time_helpers import get_time_to_expiry
import numpy as np
import pandas as pd
from math import ceil

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

    def get_ATM_multi_report(self,expr_map=None,dateRange=None):
        return self.get_ATM_multi_report_plus_x(0,expr_map=expr_map,dateRange=dateRange)

    def get_ATM_multi_report_plus_x(self,x,expr_map=None,dateRange=None):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]+float(x),0) for t in self.tickers}
        return self.get_multi_expiration_report(s_map,expr_map=expr_map,dateRange=dateRange)

    def get_ATM_multi_report_plus_x_percent(self,x,expr_map=None,dateRange=None):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]*(1+x),0) for t in self.tickers}
        return self.get_multi_expiration_report(s_map,expr_map=expr_map,dateRange=dateRange)
    
    def get_multi_expiration_report(self,strike_map,expr_map=None,dateRange=None):
        if expr_map is None and dateRange is None:
            raise ValueError("You must specify either an expiration map or a date range")
        
        if expr_map is not None and dateRange is not None:
            raise ValueError("You can specify only an expiration map or a date range, not both")
        else:
            if expr_map is not None:
                option_df = self.option_service.get_by_expr_map_and_strike_map(expr_map,strike_map)
            elif dateRange is not None:
                option_df = self.option_service.get_by_expiration_range_and_strike_map(dateRange,strike_map)
        
        if option_df.empty:
            print("Option service returned nothing")
            return option_df
        option_df = option_df.reset_index(drop=True)
        
        spots = self.spot_service.get_latest()
        strikes = [strike_map[x] for x in self.tickers]
        vol = self.spot_service.get_stdev()

        idxs = option_df.index
        symbols = option_df['contractSymbol'].apply(lambda x:x[0:x.index("2")])
        types = option_df['type']
        exprs = option_df['expiration']
        strikes = option_df['strike']
        if expr_map is None:
            expr_map = {tkr:[] for tkr in self.tickers}
            for x in range(len(exprs)):
                sym = symbols.loc[symbols.index==x].values[0]
                expr = exprs.loc[exprs.index==x].values[0]
                expr_map[sym].append(expr)
        
        
        put_BE = strikes - option_df["ask"]
        call_BE = strikes + option_df["ask"]
        
        bsmc_data = BSM_Calculator.bsm_calculation(self.tickers,spots,strike_map,vol,0.012,0,expr_map)

        ## functions in need of vectorization
        def bsmc_get(symbol,expr,typ,val_call,val_put):
            if typ == "CALL":
                out = bsmc_data.loc[((bsmc_data['expiration']==expr) & (bsmc_data['symbol']==symbol)),val_call]
            elif typ == "PUT":
                out =  bsmc_data.loc[((bsmc_data['expiration']==expr) & (bsmc_data['symbol']==symbol)),val_put]
            return out.values[0]

        def get_breakeven(idx,typ):
            if typ=="PUT":
                return put_BE[idx]
            elif typ=="CALL":
                return call_BE[idx]
        
        def get_percent_over(val1,val2):
            if val2==0:
                return 0
            val = (val1-val2)/val2
            val_sign = val/abs(val)
            return val_sign*round(abs(val),2)

        vector_bsmc_get = np.vectorize(bsmc_get)
        option_df["contractSymbol"] = symbols
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
        option_df = self.option_service.get_by_expiration_and_strike_map(expiration_date, strike_map)
        if option_df.empty:
            return option_df
        
        expr_map = {t:[expiration_date] for t in self.tickers}
        
        bsmc_data = BSM_Calculator.bsm_calculation(
            tkrs=self.tickers,
            spot=spots, 
            vol=self.spot_service.get_stdev(), 
            strikes_map=strike_map, 
            exprs_map=expr_map, 
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