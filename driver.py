from src.report_generator import ReportGenerator
import time
from datetime import date
if __name__ == '__main__':
    tickers = ['AAPL', 'AMD']# 'AMGN', 'AMZN', 'CSCO', 'FB', 'GOOG','IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']

    rfr = 0.012  # risk free rate
    #lower and upper date cutoffs
    expr_begin = "2021-03-01"
    expr_end = "2021-05-03"
    # initialize report generator for tickers
    report = ReportGenerator(tickers, rfr).get_ATM_multi_report(dateRange=(expr_begin,expr_end))
    print(report)
    # ReportGenerator(tickers, rfr).get_ATM_multi_report_plus_x_percent(-.4,(None,endDate)).to_csv('reports/report_ATM_-40%_' + str(date.today())+'.csv')
