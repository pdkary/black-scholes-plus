from datetime import datetime
from src.report_generator import ReportGenerator

class FTSTrader:
    def __init__(self,tickers,rfr,percent_above_below):
        self.tickers = tickers
        self.rfr = rfr
        self.percent_above_below = percent_above_below
        self.rg = ReportGenerator(tickers,rfr)
    
    #should take about 2 minutes...
    def refresh_data(self):
        self.below_ATM = rg.get_ATM_multi_report_plus_x_percent(-self.percent_above_below)
        self.above_ATM = rg.get_ATM_multi_report_plus_x_percent(self.percent_above_below)
        self.ATM = rg.get_ATM_multi_report()

    @staticmethod
    def get_fts_option_key(tkr,type,expr,strike):
        type_id = "D" if type=="CALL" else "P"
        expr_date = datetime.strptime(expr_date,"%Y-%m-%d")
        yr = str(datetime.year())[2:]
        strike_str = str(strike)
        if strike < 100:
            strike_str = "0"+strike_str
        if strike < 1000:
            strike_str = strike_str + "00"
        if strike > 1000:
            strike_str = strike_str+"0"
        return tkr+type_id+expr_date.day()+strike_str