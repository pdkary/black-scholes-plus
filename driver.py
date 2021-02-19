from src.report_generator import ReportGenerator
import time
from datetime import date
if __name__ == '__main__':
    tickers = ['AAPL', 'AMD', 'AMGN', 'AMZN', 'CSCO', 'FB','GOOG', 'IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']

    rfr = 0.012 #risk free rate
    #initialize report generator for tickers
    rg = ReportGenerator(tickers,rfr)
    #Get report for at the money prices
    tic = time.perf_counter()
    report_atm = rg.get_ATM_multi_report_plus_x_percent(.05)
    ##write to csv
    report_atm.to_csv('reports/report_' + str(date.today())+'.csv')
    toc = time.perf_counter()
    print("Analyzed {} options in {} seconds".format(len(report_atm.index),toc-tic))