from src.BSM_calculator import BSM_Calculator
from src.strike_optimizer import StrikeOptimizer
if __name__ == '__main__':
    tickers = ['IYZ', 'AAPL', 'AMD', 'AMGN', 'AMZN', 'BCE', 'CSCO', 'FB','GOOG', 'IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP', 'VZ']
    strike_map = {'IYZ':50,'AAPL':200,'AMD':120,'AMGN':400,'AMZN':3600,'BCE':60,'CSCO':60,'FB':300,'GOOG':2200,'IBM':150,'INTC':70,'MSFT':300,'MU':100,'NFLX':600,'NVDA':650,'SHOP':1750,'VZ':75}

    expiration_date = "2021-03-19"
    so = StrikeOptimizer(tickers,interval='1h')
    so.get_percent_above(strike_map,expiration_date,0.012,0)
    # bsmc = BSM_Calculator(tickers,interval='1h')
    # bsmc_data = bsmc.get_report(expiration_date,strike_map,0.012,0)

    # print("-"*56+ "BSMC DATA"+"-"*56)
    # print(bsmc_data)
    # print("-"*(56*2+9))