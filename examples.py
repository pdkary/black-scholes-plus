from src.report_generator import ReportGenerator

tickers = ['AAPL', 'GOOG', 'NVDA']

def specified_strikes_and_expirations():
    strikes = {'AAPL':140,'GOOG':2200,'NVDA':610}
    expr_date = "2021-09-17"
    rg = ReportGenerator(tickers,0.012)
    rg.get_report(expr_date,strikes).to_csv("outputfilename.csv")

def specified_strikes_no_expirations():
    strikes = {'AAPL':140,'GOOG':2200,'NVDA':610}
    rg = ReportGenerator(tickers,0.012)
    rg.get_multi_expiration_report(strikes).to_csv("outputfilename.csv")

def ATM_strikes_with_expiration():
    expr_date = "2021-09-17"
    rg = ReportGenerator(tickers,0.012)
    rg.get_ATM_report(expr_date).to_csv("outputfilename.csv")

def ATM_strikes_no_expiration():
    rg = ReportGenerator(tickers,0.012)
    rg.get_ATM_multi_report().to_csv("outputfilename.csv")

def ATM_strikes_plus_absolute_x_with_expirations():
    expr_date = "2021-09-17"
    rg = ReportGenerator(tickers,0.012)
    rg.get_ATM_plus_x(expr_date,10).to_csv("outputfilename.csv")

def ATM_strikes_plus_relative_x_with_expirations():
    expr_date = "2021-09-17"
    rg = ReportGenerator(tickers,0.012)
    rg.get_ATM_plus_x_percent(expr_date,.10).to_csv("outputfilename.csv")

def ATM_strikes_plus_absolute_x_no_expirations():
    rg = ReportGenerator(tickers,0.012)
    rg.get_ATM_multi_report_plus_x(10).to_csv("outputfilename.csv")

def ATM_strikes_plus_relative_x_no_expirations():
    rg = ReportGenerator(tickers,0.012)
    rg.get_ATM_multi_report_plus_x_percent(.10).to_csv("outputfilename.csv")