
import yfinance as yf
import pandas as pd

class OptionDataService:
    desired_columns = ['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility']
    output_columns = ['contractSymbol','expiration','type', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility']

    def __init__(self,tickers):
        self.tickers = tickers
        self.yf_tickers = {t:yf.Ticker(t) for t in self.tickers}
    
    ## returns a matrix of (NxM) Tkrs: [expr_dates (padded with 0's to the longest entry)]
    def get_expiration_dates(self):
        raw_data = {tkr:list(self.yf_tickers[tkr].options) for tkr in self.tickers}
        max_len = max([len(raw_data[tkr]) for tkr in self.tickers])
        raw_data = {tkr:raw_data[tkr]+ [0]*(max_len - len(raw_data[tkr])) for tkr in self.tickers}
        return pd.DataFrame(raw_data)
    
    def get_data(self,expiration_date,strike_map):
        option_df = pd.DataFrame()
        for t in self.tickers:
            tkr_option_data = self.get_single_ticker(t,expiration_date,strike_map[t])
            if not tkr_option_data.empty:
                option_df = option_df.append(tkr_option_data)
        option_df = option_df.reset_index(drop=True)
        if not option_df.empty:
            return option_df[self.output_columns]
        return option_df
    
    def get_single_ticker(self,ticker,expiration,strike):
        output_df = pd.DataFrame()
        if expiration==0:
            return output_df
        try:
            option_chain = self.yf_tickers[ticker].option_chain(expiration)
        except ValueError as e:
            print("failed on ({},{},{})".format(ticker,expiration,strike))
            return output_df
        
        call_chain = option_chain.calls
        call_row = call_chain.loc[call_chain['strike']==strike]
        call_row = call_row.loc[call_row["openInterest"]!=0]
        call_row = call_row[self.desired_columns]
        call_row['expiration'] = [expiration for i in range(len(call_row['bid']))]
        call_row['type'] = ['CALL' for i in range(len(call_row['bid']))]

        put_chain = option_chain.puts
        put_row = put_chain.loc[put_chain['strike']==strike]
        put_row = put_row.loc[put_row["openInterest"]!=0]
        put_row = put_row[self.desired_columns]
        put_row['expiration'] = [expiration for i in range(len(put_row['bid']))]
        put_row['type'] = ['PUT' for i in range(len(put_row['bid']))]

        if not call_row.empty:
            output_df = output_df.append(call_row)
        if not put_row.empty:
            output_df = output_df.append(put_row)
        
        return output_df
    
    def get_all_expiration_data(self,strike_map):
        output_df = pd.DataFrame()
        exp_dates = self.get_expiration_dates()
        for t in self.tickers:
            for d in exp_dates[t]:
                expr_data = self.get_single_ticker(t,d,strike_map[t])
                if not expr_data.empty:
                    output_df = output_df.append(expr_data)
        
        return output_df
    