from src.report_generator import ReportGenerator

tickers = ['AAPL', 'GOOG', 'NVDA']

expr_date = "2021-09-17"
rfr = 0.012 #risk free rate
#initialize report generator for tickers
rg = ReportGenerator(tickers,rfr)
#Get report for at the money prices
report_atm = rg.get_ATM_report(expr_date)
print(report_atm)