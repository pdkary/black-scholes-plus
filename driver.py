from src.report_generator import ReportGenerator
import time
from datetime import date
if __name__ == '__main__':
    tickers = ['AAPL', 'AMD', 'AMGN', 'AMZN', 'CSCO', 'FB', 'GOOG','IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']

    expr_date = "2021-12-17"
    rfr = 0.012  # risk free rate
    # initialize report generator for tickers
    ReportGenerator(tickers, rfr).get_ATM_report(expr_date).to_csv('reports/report_' + str(date.today())+'.csv')
