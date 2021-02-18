from src.report_generator import ReportGenerator

if __name__ == '__main__':
    tickers = ['IYZ', 'AAPL', 'AMD', 'AMGN', 'AMZN', 'BCE', 'CSCO', 'FB','GOOG', 'IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP', 'VZ']
    strike_map = {'IYZ':50,'AAPL':200,'AMD':120,'AMGN':400,'AMZN':3600,'BCE':60,'CSCO':60,'FB':300,'GOOG':2200,'IBM':150,'INTC':70,'MSFT':300,'MU':100,'NFLX':600,'NVDA':650,'SHOP':1750,'VZ':75}

    # expiration_date = "2021-05-21"
    expiration_date = "2021-02-19"
    rg = ReportGenerator(tickers,rfr=0.012)
    report = rg.get_ATM_report(expiration_date)
    print(report)
    