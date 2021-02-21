from src.data_collector import DataCollector

tickers = ['AAPL', 'AMD', 'AMGN', 'AMZN', 'CSCO', 'FB', 'GOOG','IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']
filename = "collected_data.csv"
    
dc = DataCollector(tickers,filename,.012)
dc.update()