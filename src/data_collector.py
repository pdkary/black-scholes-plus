
from src.report_generator import ReportGenerator
from datetime import datetime
import pandas as pd
import time
"""
Ok so finding historical option data online is either really hard or really expensive
So for training, im gonna let this run on a raspberry pi for a few months
"""
class DataCollector:
    """
    Tickers: list of tickers who's options you want to trade
    filename: output csv
    rfr: risk free rate
    """
    def __init__(self,tickers,filename,rfr):
        self.tickers = tickers
        self.filename = filename
        self.rfr = rfr
        self.rg = ReportGenerator(tickers,rfr)
    
    def update(self,percent_above_below):
        below_ATM = self.rg.get_ATM_multi_report_plus_x_percent(percent_above_below)
        above_ATM = self.rg.get_ATM_multi_report_plus_x_percent(percent_above_below)
        ATM = self.rg.get_ATM_multi_report()

        below_ATM['Date Retrieved'] = [datetime.now() for i in range(len(below_ATM.index))]
        above_ATM['Date Retrieved'] = [datetime.now() for i in range(len(above_ATM.index))]
        ATM['Date Retrieved'] = [datetime.now() for i in range(len(ATM.index))]

        existing_data = pd.read_csv(self.filename)

        existing_data = existing_data.append(below_ATM)
        existing_data = existing_data.append(above_ATM)
        existing_data = existing_data.append(ATM)

        existing_data.to_csv(self.filename)
