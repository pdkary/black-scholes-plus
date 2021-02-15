from src.BSM_calculator import BSM_Calculator

tickers = ['AAPL', 'GOOG', 'NVDA']
strike_map = {'AAPL':200,'GOOG':1220,'NVDA':650}

bsmc = BSM_Calculator(tickers,interval='1d')

rfr = 0.012 #risk free rate
dyield = 0 #dividend yield

bsmc_data = bsmc.get_report("2021-03-19",strike_map,rfr,dyield)
print(bsmc_data)