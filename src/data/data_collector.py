
from src.report_generator import ReportGenerator
from datetime import datetime
import pandas as pd
import time
"""
Ok so finding historical option data online is either really hard or really expensive
So for training, im gonna let this run on a raspberry pi for a few months
"""
class DataCollector:
    df_cols = ['contractSymbol','expiration','type','spot','strike','BSM Value','BSM% over ask', 'lastPrice', 'bid', 'ask', 'B/E','d% for BE','openInterest','Delta','Gamma','Theta','Vega','Rho','impliedVolatility', 'Annual Vol']
    """
    Tickers: list of tickers who's options you want to trade
    filename: output csv
    rfr: risk free rate
    """
    def __init__(self,tickers,filename,rfr,last_expiry_date=None):
        self.tickers = tickers
        self.filename = filename
        self.rfr = rfr
        self.rg = ReportGenerator(tickers,rfr)
        self.end_expiry = last_expiry_date
    
    def update(self,percent_above_below):
        print("gathering below ATM")
        below_ATM = self.rg.get_ATM_multi_report_plus_x_percent(percent_above_below,self.end_expiry)
        print("gathering above ATM")
        above_ATM = self.rg.get_ATM_multi_report_plus_x_percent(percent_above_below,self.end_expiry)
        print("gathering ATM")
        ATM = self.rg.get_ATM_multi_report(self.end_expiry)

        print('retrieval complete')
        below_ATM['Date Retrieved'] = [datetime.now() for i in range(len(below_ATM.index))]
        above_ATM['Date Retrieved'] = [datetime.now() for i in range(len(above_ATM.index))]
        ATM['Date Retrieved'] = [datetime.now() for i in range(len(ATM.index))]

        try:
            existing_data = pd.read_csv(self.filename)
        except pd.errors.EmptyDataError:
            existing_data = pd.DataFrame()

        existing_data = existing_data.append(below_ATM)
        existing_data = existing_data.append(above_ATM)
        existing_data = existing_data.append(ATM)

        existing_data = existing_data[self.df_cols]
        existing_data = existing_data.reset_index(drop=True)
        existing_data.to_csv(self.filename)
