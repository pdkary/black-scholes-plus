from src.spot_data_service import SpotDataService
from src.option_data_service import OptionDataService
from src.BSM_calculator import BSM_Calculator
import numpy as np
from math import ceil

class ReportGenerator:
    def __init__(self, tickers,rfr):
        self.tickers = tickers
        self.rfr = rfr
        self.spot_service = SpotDataService(tickers)
        self.option_service = OptionDataService(tickers)

    def get_ATM_report(self,expiration_date):
        return self.get_ATM_plus_x(expiration_date,0)

    def get_ATM_plus_x(self,expiration_date,x):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]+x,1) for t in self.tickers}
        return self.get_report(expiration_date,s_map)

    def get_ATM_plus_x_percent(self,expiration_date,x):
        latest = self.spot_service.get_latest()
        s_map = {t:round(latest[t]*(1+x),1) for t in self.tickers}
        return self.get_report(expiration_date,s_map)

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

        display_cols = ['contractSymbol', 'type','spot','strike','BSM Value', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility', 'Annual Vol']

        return option_df[display_cols].round(4)
    
    def get_around_ATM_report(self,expiration_date,step):
        
        percent_range = [step*x for x in range(-5,5)]
        for i in percent_range:
            c = "+" if i > 0 else "-"
            print("-"*56+"("+c+str(abs(i)) + "%)" + "-"*56)
            try:
                report = self.get_ATM_plus_x_percent(expiration_date,i/100)
                print(report)
            except IndexError:
                print("Nothing to show")
                continue