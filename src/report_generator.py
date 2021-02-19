from src.spot_data_service import SpotDataService
from src.option_data_service import OptionDataService
from src.BSM_calculator import BSM_Calculator
import numpy as np
from math import ceil

class ReportGenerator:
    display_cols = ['contractSymbol','expiration','type','spot','strike','BSM Value','BSM% over ask', 'lastPrice', 'bid', 'ask', 'B/E','d% for BE','openInterest', 'impliedVolatility', 'Annual Vol']

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
        s_map = {t:round(latest[t]*(1+x),1) for t in self.tickers}
        return self.get_report(expiration_date,s_map)

    def get_ATM_multi_report(self):
        return self.get_ATM_multi_report_plus_x(0)

    def get_ATM_multi_report_plus_x(self,x):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]+x,0) for t in self.tickers}
        return self.get_multi_expiration_report(s_map)

    def get_ATM_multi_report_plus_x_percent(self,x):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]*(1+x),1) for t in self.tickers}
        return self.get_multi_expiration_report(s_map)
    
    def get_multi_expiration_report(self,strike_map):
        latest = self.spot_service.get_latest()
        spots = {t:round(latest[t]) for t in self.tickers}

        option_df = self.option_service.get_all_expiration_data(strike_map)
        option_df = option_df.reset_index(drop=True)
        expr_dates = self.option_service.get_expr_dates()

        bsmc_map = self.get_bsmc_map(expr_dates,spots)
        idxs = option_df.index
        symbols = option_df['contractSymbol'].apply(lambda x:x[0:x.index("2")])
        exprs = option_df['expiration']
        types = option_df['type']
        
        put_BE = option_df["strike"] - option_df["ask"]
        call_BE = option_df["strike"] + option_df["ask"]

        ## functions in need of vectorization
        def get_val(symbol, expr,type ):
            if type == "CALL":
                return bsmc_map[expr]["Call value"][symbol]
            elif type == "PUT":
                return bsmc_map[expr]["Put value"][symbol]

        def get_vol(symbol,expr):
            return bsmc_map[expr]["Annual Vol"][symbol]

        def get_breakeven(idx,type):
            if type=="PUT":
                return put_BE[idx]
            elif type=="CALL":
                return call_BE[idx]
        
        def get_percent_over(val1,val2):
            val = (val1-val2)/val2
            val_sign = val/abs(val)
            return val_sign*round(abs(val),2)

        option_df["BSM Value"] = np.vectorize(get_val)(symbols,exprs,types).round(2)
        option_df["Annual Vol"] = np.vectorize(get_vol)(symbols,exprs)
        option_df["B/E"] = np.vectorize(get_breakeven)(idxs,types)
        option_df["spot"] = symbols.apply(lambda x: spots[x])
        option_df['d% for BE'] = round((option_df['B/E'] - option_df['spot'])/option_df['spot'],2)
        option_df['BSM% over ask'] = np.vectorize(get_percent_over)(option_df['BSM Value'],option_df['ask'])
        return option_df[self.display_cols]
    
    ## get a map of {expiration_dates -> {tkr -> bsm_val}} 
    def get_bsmc_map(self,expr_dates,strike_map):
        spots = self.spot_service.get_latest()
        vol = self.spot_service.get_stdev()
        bsmc_map = {}
        for t in self.tickers:
            for e in expr_dates[t]:
                if e not in bsmc_map:
                    bsmc_map[e] = BSM_Calculator.bsm_calculation(spots,vol,strike_map,e,self.rfr,0)
        return bsmc_map

    def get_report(self, expiration_date, strike_map):
        spots = self.spot_service.get_latest()
        option_df = self.option_service.get_data(expiration_date, strike_map)
        bsmc_data = BSM_Calculator.bsm_calculation(
            spot=spots, 
            vol=self.spot_service.get_stdev(), 
            strike_map=strike_map, 
            expr_date=expiration_date, 
            rfr=self.rfr,
            div_yield=0)

        symbols = option_df['contractSymbol']
        types = option_df['type']

        def get_val(symbol, type):
            if type == "CALL":
                return bsmc_data["Call value"][symbol]
            elif type == "PUT":
                return bsmc_data["Put value"][symbol]

        option_df["BSM Value"] = np.vectorize(get_val)(symbols, types).round(2)
        option_df["Annual Vol"] = symbols.apply(lambda x: bsmc_data["Annual Vol"][x])
        option_df["spot"] = symbols.apply(lambda x: spots[x])


        return option_df[self.display_cols].round(4)