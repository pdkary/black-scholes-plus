
import yfinance as yf
import pandas as pd

class OptionDataService:
    desired_columns = ['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility']
    def __init__(self,tickers):
        self.tickers = tickers
    
    def get_data(self,expiration_date,strike_map):
        option_chains = {t: yf.Ticker(t).option_chain(expiration_date) for t in self.tickers}
        option_df = pd.DataFrame()

        for t in self.tickers:
            call_chain = option_chains[t].calls
            call_row = call_chain.loc[call_chain['strike']==strike_map[t]]
            call_row = call_row[self.desired_columns]
            call_row['contractSymbol'] = call_row['contractSymbol'].apply(lambda x: x[0:x.index('2')])
            call_row['type'] = ['CALL' for i in range(len(call_row['bid']))]

            put_chain = option_chains[t].puts
            put_row = put_chain.loc[put_chain['strike']==strike_map[t]]
            put_row = put_row[self.desired_columns]
            put_row['contractSymbol'] = put_row['contractSymbol'].apply(lambda x: x[0:x.index('2')])
            put_row['type'] = ['PUT' for i in range(len(put_row['bid']))]

            if not call_row.empty:
                option_df = option_df.append(call_row)
            if not put_row.empty:
                option_df = option_df.append(put_row)
        
        option_df = option_df.reset_index(drop=True)
        cols = option_df.columns.tolist()
        cols = [cols[0],cols[-1]] + cols[1:-1]
        return option_df[cols]
    
