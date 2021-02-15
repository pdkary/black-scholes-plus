from src.BSM_calculator import BSM_Calculator
import numpy as np
class StrikeOptimizer:
    def __init__(self,tickers,interval):
        self.tickers = tickers
        self.interval = interval
        self.bsmc = BSM_Calculator(tickers,interval)

    def get_percent_above(self,initial_strikes,expiration_date,rfr,div_yield):
        option_data = self.bsmc.get_report(expiration_date,initial_strikes,rfr,div_yield)
        
        ##Goal here is to perform gradient descent on the strike prices
        ## optimization variable: maximize BSM value  - lastPrice
        print("-"*56+ "BSMC DATA"+"-"*56)
        print(option_data)
        print("-"*(56*2+9))
        print("\n")
        print("-"*50+ "UNDERVALUED OPTIONS"+"-"*50)
        print(option_data.loc[option_data['BSM Value'] >= option_data['ask']])
        print("-"*(56*2+9))