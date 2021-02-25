from src.data.data_collector import DataCollector
from datetime import datetime
tickers = ['AAPL', 'AMD', 'AMGN', 'AMZN', 'CSCO', 'FB', 'GOOG','IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']
filename = "collected_data.csv"
last_possible_expiry = "2021-05-03"
trading_days = [0,1,2,3,4]

now = datetime.now()
if (now.weekday() in trading_days) and (now.hour < 18) and (now.hour > 8):
    dc = DataCollector(tickers,filename,.012,last_possible_expiry)
    dc.update(.1)