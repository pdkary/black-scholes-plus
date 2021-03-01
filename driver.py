from src.report_generator import ReportGenerator
import time
from datetime import date
if __name__ == '__main__':
    tickers = ['AAPL', 'AMD'],# 'AMGN', 'AMZN', 'CSCO', 'FB', 'GOOG','IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']

    rfr = 0.012  # risk free rate
    #lower and upper date cutoffs
    expr = "2021-05-03"
    expr_map = {tkr:expr for tkr in tickers}
    # initialize report generator for tickers
    ReportGenerator(tickers, rfr).get_ATM_multi_report(expr_map).to_csv('reports/report_ATM_' + str(date.today())+'.csv')
    # ReportGenerator(tickers, rfr).get_ATM_multi_report_plus_x_percent(-.4,(None,endDate)).to_csv('reports/report_ATM_-40%_' + str(date.today())+'.csv')
