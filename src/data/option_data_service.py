
import yfinance as yf
import pandas as pd
from datetime import datetime
from numbers import Number
from numpy import uint8

class OptionDataService:
    desired_columns = ['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'inTheMoney', 'openInterest', 'impliedVolatility']
    output_columns = ['contractSymbol','expiration','type', 'strike', 'lastPrice', 'bid', 'ask', 'openInterest', 'impliedVolatility']

    def __init__(self,tickers):
        self.tickers = tickers
        self.yf_tickers = {t:yf.Ticker(t) for t in self.tickers}

    """
    expiration_map => {tkr: [exp1,exp2,...,expN]}
    strike_map     => {tkr:strike}
    """
    def get_by_expr_map_and_strike_map(self,expiration_map,strike_map):
        option_df = pd.DataFrame()
        for t in self.tickers:
            strike = strike_map[t]
            exps = expiration_map[t]
            if type(exps) is list:
                if type(strike) is list:
                    for s in strike:
                        for ex in exps:
                            op_data = self.get_by_ticker_expiration_and_strike(t,ex,s)
                            option_df = option_df.append(op_data)
                elif isinstance(strike,Number):
                    for ex in exps:
                            op_data = self.get_by_ticker_expiration_and_strike(t,ex,s)
                            option_df = option_df.append(op_data)
            elif type(exps) is str:
                if type(strike) is list:
                    for s in strike:
                        op_data = self.get_by_ticker_expiration_and_strike(t,exps,s)
                        option_df = option_df.append(op_data)
                elif isinstance(strike,Number):
                    op_data = self.get_by_ticker_expiration_and_strike(t,exps,strike)
                    option_df = option_df.append(op_data)
        
        option_df = option_df.reset_index(drop=True)
        if not option_df.empty:
            return option_df[self.output_columns]
        return option_df

    def get_by_expiration_and_strike_map(self,expiration_date,strike_map):
        expr_map = {t:expiration_date for t in self.tickers}
        return self.get_by_expr_map_and_strike_map(expr_map,strike_map)

    def get_by_expiration_range_and_strike_map(self,dateRange,strike_map):
        output_df = pd.DataFrame()
        exp_dates = self.get_expiration_dates(dateRange)
        for t in self.tickers:
            for d in exp_dates[t]:
                expr_data = self.get_by_ticker_expiration_and_strike(t,d,strike_map[t])
                if not expr_data.empty:
                    output_df = output_df.append(expr_data)
        
        return output_df

     ## returns a matrix of (NxM) Tkrs: [expr_dates (padded with 0's to the longest entry)]
    
    def get_expiration_dates(self,dateRange=None):
        raw_data = {tkr:list(self.yf_tickers[tkr].options) for tkr in self.tickers}
        if dateRange is not None:
            start_datetime = datetime.strptime(dateRange[0],'%Y-%m-%d')
            end_datetime = datetime.strptime(dateRange[1],'%Y-%m-%d')
            for tkr in self.tickers:
                for i in range(len(raw_data[tkr])):
                    expr_date = datetime.strptime(raw_data[tkr][i],'%Y-%m-%d')
                    if end_datetime < expr_date or start_datetime > expr_date:
                        raw_data[tkr][i]=0

        for tkr in self.tickers:
            raw_data[tkr] = list(filter(lambda x: x!=0,raw_data[tkr]))

        max_len = max([len(raw_data[tkr]) for tkr in self.tickers])
        raw_data = {tkr:raw_data[tkr]+ [0]*(max_len - len(raw_data[tkr])) for tkr in self.tickers}
        return pd.DataFrame(raw_data)
    
    def get_by_ticker_expiration_and_strike(self,ticker,expiration,strike):
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
        
        # call_row = call_row.loc[call_row["openInterest"]!=0]
        call_row = call_row[self.desired_columns]
        call_row['expiration'] = [expiration for i in range(len(call_row['bid']))]
        call_row['type'] = ['CALL' for i in range(len(call_row['bid']))]

        put_chain = option_chain.puts
        put_row = put_chain.loc[put_chain['strike']==strike]
        put_row = put_row.loc[put_row["openInterest"]!=0]
        put_row = put_row[self.desired_columns]
        put_row['expiration'] = [expiration for i in range(len(put_row['bid']))]
        put_row['type'] = ['PUT' for i in range(len(put_row['bid']))]

        output_df = output_df.append(call_row)
        output_df = output_df.append(put_row)
        return output_df
    
    