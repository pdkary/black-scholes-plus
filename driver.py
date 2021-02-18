from src.report_generator import ReportGenerator

if __name__ == '__main__':
    tickers = ['IYZ', 'AAPL', 'AMD', 'AMGN', 'AMZN', 'BCE', 'CSCO', 'FB','GOOG', 'IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP', 'VZ']

    # expiration_date = "2023-03-17"
    expiration_date = "2021-02-19"
    rg = ReportGenerator(tickers,rfr=0.012)
    report = rg.get_ATM_plus_x(expiration_date,10)
    print(report)
    