from src.utils.transaction_logger import TranactionLogger, TransactionActions, TransactionTypes
from src.utils.time_helpers import timestamp_to_string
from src.data.option_data_service import OptionDataService
from src.data.spot_data_service import SpotDataService
from src.report_generator import ReportGenerator
import numpy as np
import pandas as pd
import yfinance as yf
from math import isnan

class PortfolioCalculator(TranactionLogger):
    needed_columns = ["contractSymbol","expiration","type","spot","strike","BSM Value","lastPrice","Delta"]
    def __init__(self, filename=None):
        TranactionLogger.__init__(self, filename)

    def analyze_portfolio(self):
        sec_tickers = self.get_all_tkrs()
        rg = ReportGenerator(sec_tickers, .012)

        opt_tickers = self.get_all_opt_tkrs()
        opt_data = {t: self.get_all_options_by_tkr(t) for t in opt_tickers}

        vector_t2s = np.vectorize(timestamp_to_string)
        expr_map = {
            t: list(set(vector_t2s(opt_data[t]['expiration'].values))) for t in opt_tickers}
        strike_map = {
            t: list(set(opt_data[t]['strike'].values)) for t in opt_tickers}

        option_status = rg.get_multi_expiration_report(strike_map, expr_map)[self.needed_columns]
        sec_betas = {tkr:rg.option_service.yf_tickers[tkr].get_info()['beta'] for tkr in sec_tickers}
        weighted_p = self.get_weighted_portfolio()
        ##----filter option data to only whats in our portfolio---#
        def is_in_p(tkr,typ,strike):
            matches = weighted_p.loc[(weighted_p['symbol']==tkr) & (weighted_p['type']==typ) & (weighted_p['strike']==strike)]
            return len(matches)>0
        
        is_in_ps = np.vectorize(is_in_p)(option_status['contractSymbol'],option_status['type'],option_status['strike'])
        option_status = option_status.loc[is_in_ps]
        ##------------------------------ BETA CALCULATION ------------------------------##
        def get_beta(tkr,typ,strike):
            if typ=='security':
                return sec_betas[tkr]
            elif typ=='CALL' or typ=='PUT':
                row = option_status.loc[(option_status['contractSymbol']==tkr) & (option_status['type']==typ) & (option_status['strike']==strike)]
                spot = row['spot']
                delta = row['Delta']
                last = row['lastPrice']
                return (spot/last)*delta*sec_betas[tkr]

        def get_delta(tkr,typ,strike):
            if typ=='security':
                return 0
            elif typ=='CALL' or typ=='PUT':
                delta = 100.0*option_status.loc[(option_status['contractSymbol']==tkr) & (option_status['type']==typ) & (option_status['strike']==strike)]['Delta']
                return float(delta.values[0])

        def get_last(tkr,typ,strike):
            if typ=='security':
                return option_status.loc[(option_status['contractSymbol']==tkr)]['spot'].values[0]
            elif typ=='CALL' or typ=='PUT':
                last = option_status.loc[(option_status['contractSymbol']==tkr) & (option_status['type']==typ) & (option_status['strike']==strike)]['lastPrice']
                return float(last.values[0])

        weighted_p['beta'] = np.vectorize(get_beta)(weighted_p['symbol'],weighted_p['type'],weighted_p['strike'])
        weighted_p['weighted beta'] = np.vectorize(lambda x,y:x*y)(weighted_p['weight'],weighted_p['beta'])
        weighted_p['% delta'] = np.vectorize(get_delta)(weighted_p['symbol'],weighted_p['type'],weighted_p['strike'])
        weighted_p['last'] = np.vectorize(get_last)(weighted_p['symbol'],weighted_p['type'],weighted_p['strike'])
        return weighted_p
        
    def get_tkr_vwap(self, tkr):
        tkr_sec_data = self.get_all_securities_by_tkr(tkr)
        buys = tkr_sec_data.loc[tkr_sec_data['action']
                                == TransactionActions.BUY]
        sells = tkr_sec_data.loc[tkr_sec_data['action']
                                 == TransactionActions.SELL]

        buys_x_volume = (buys['price']*buys['qty']).sum()
        buy_volume = buys['qty'].sum()
        buy_vwap = buys_x_volume/buy_volume if buy_volume > 0 else 0

        sells_x_volume = (sells['price']*sells['qty']).sum()
        sell_volume = sells['qty'].sum()
        sell_vwap = sells_x_volume/sell_volume if sell_volume > 0 else 0
        return (buy_vwap, sell_vwap)

    def get_option_profit_function(self, tkr):
        tkr_opt = self.get_all_options_by_tkr(tkr)

        def get_func(typ, strike, action, cost, qty):
            m = -1 if action == TransactionActions.SHORT_SELL else 1
            if typ == TransactionTypes.CALL:
                return lambda x: m*qty*100*(max(0, x-strike)-cost)
            if typ == TransactionTypes.PUT:
                return lambda x: m*qty*100*(max(0, strike-x)-cost)

        funcs = np.vectorize(get_func)(
            tkr_opt['type'], tkr_opt['strike'], tkr_opt['action'], tkr_opt['price'], tkr_opt['qty'])
        return lambda x: sum(f(x) for f in funcs)
