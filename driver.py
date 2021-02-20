from src.report_generator import ReportGenerator
import time
from datetime import date
if __name__ == '__main__':
    tickers = ['AAPL', 'AMD', 'AMGN', 'AMZN', 'CSCO', 'FB', 'GOOG','IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']

    rfr = 0.012  # risk free rate
    # initialize report generator for tickers
    ReportGenerator(tickers, rfr).get_ATM_multi_report_plus_x(.01).to_csv('reports/report_' + str(date.today())+'.csv')
