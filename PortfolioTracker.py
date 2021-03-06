from src.utils.PortfolioCalculator import PortfolioCalculator, TransactionActions, TransactionTypes
from datetime import datetime


def format_date(d):
    return datetime.strptime(d, "%Y-%m-%d,%I:%M:%S %p")


expr_date = format_date("2021-04-16,12:00:00 AM")
pc = PortfolioCalculator()
pc.buy_security("IBM", format_date("2021-02-01,3:19:59 PM"), 120.61, 500)

pc.buy_call("AAPL", format_date("2021-02-23,12:17:42 PM"),expr_date, 1.42, 140, 100)
pc.buy_call("IBM", format_date("2021-02-23,12:19:17 PM"),expr_date, 1.24, 130, 100)

pc.buy_put("FB", format_date("2021-02-23,12:24:25 PM"),expr_date, 5.25, 240, 100)
pc.short_put("FB", format_date("2021-02-23,12:24:42 PM"),expr_date, 7.75, 250, 100)
pc.short_call("FB", format_date("2021-02-23,12:25:16 PM"),expr_date, 10.55, 270, 100)
pc.buy_call("FB", format_date("2021-02-23,12:25:32 PM"), expr_date, 7.05, 280, 100)

pc.buy_call("GOOG", format_date("2021-02-25,1:06:48 PM"),expr_date,32.60,2200,10)
pc.buy_call("NFLX", format_date("2021-02-25,1:23:12 PM"),expr_date,28.9,550,10)

pc.buy_security("SHOP",format_date("2021-03-01,11:52:11 AM"),1660.19,30)
pc.buy_security("SHOP",format_date("2021-03-01,11:52:36 AM"),1661.38,30)

pc.buy_put("SHOP",format_date("2021-03-02,9:30:00 AM"),expr_date,253.3,1900,30)

pf = pc.get_option_profit_function('FB')
report = pc.analyze_portfolio()
print(report)
total_sec = report.loc[report['type']=='security']['invested'].sum()
beta_times_invested = (report.loc[report['type']=='security']['beta']*report.loc[report['type']=='security']['invested']).sum()
print("Securities Beta: {}".format(beta_times_invested/total_sec))
print("Portfolio Beta: {}".format(report['weighted beta'].sum()))
print("Portfolio Delta: {}".format(report['% delta'].sum()/100.0))