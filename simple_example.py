from src.report_generator import ReportGenerator

tickers = ['AAPL', 'GOOG', 'NVDA']
strike_map = {'AAPL':200,'GOOG':1220,'NVDA':650}

expr_date = "2021-02-19"
rfr = 0.012 #risk free rate

#Get report using specified strikes
rg = ReportGenerator(tickers,rfr)
report = rg.get_report(expr_date,strike_map)
print(report)
#Get report for at the money prices
report_atm = rg.get_ATM_report(expr_date)