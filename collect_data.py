from src.data_collector import DataCollector

tickers = ['AAPL', 'AMD', 'AMGN', 'AMZN', 'CSCO', 'FB', 'GOOG','IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']
filename = "collected_data.csv"
last_possible_expiry = "2021-05-03"
    
dc = DataCollector(tickers,filename,.012,last_possible_expiry)
dc.update(.1)