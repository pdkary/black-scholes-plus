from utils.transaction_logger import TranactionLogger, TransactionActions, TransactionTypes
from utils.time_helpers import timestamp_to_string
from data.option_data_service import OptionDataService
from data.spot_data_service import SpotDataService
from report_generator import ReportGenerator
from math import nan
import numpy as np
import pandas as pd


class PortfolioCalculator(TranactionLogger):
    def __init__(self, filename=None):
        TranactionLogger.__init__(self, filename)

    def analyze_portfolio(self):
        sec_tickers = self.get_all_tkrs()
        rg = ReportGenerator(sec_tickers, .012)

        opt_tickers = self.get_all_opt_tkrs()
        vector_t2s = np.vectorize(timestamp_to_string)
        opt_data = {t: self.get_all_options_by_tkr(t) for t in opt_tickers}

        expr_map = {
            t: list(set(vector_t2s(opt_data[t]['expiration'].values))) for t in opt_tickers}
        strike_map = {
            t: list(set(opt_data[t]['strike'].values)) for t in opt_tickers}

        spot_data = rg.spot_service.get_latest()
        option_status = rg.get_multi_expiration_report(strike_map, expr_map)
        option_position_report = pd.DataFrame(dtype=object)
        i=0
        for t in sec_tickers:
            for s in opt_data[t]['strike'].values:
                match = opt_data[t].loc[(opt_data[t]['strike']== s)]
                typ = match['type'].values[0].upper()
                action = match['action'].values[0]
                price = match['price'].values[0]
                qty = match['qty'].values[0]
                for e in expr_map[t]:
                    m = option_status.loc[(option_status['contractSymbol'] == t) & (option_status['type'] == typ) & (
                        option_status['expiration'] == e) & (option_status['strike'] == s)]
                    tmp = pd.DataFrame({'symbol':t,'expiration':e,'type':typ,'strike':s,'BSM Value':m['BSM Value'].values[0],'last':m['lastPrice'].values[0],'action':action,'paid':price,'qty':qty,'delta':m['Delta'].values[0],'gamma':m['Gamma'].values[0],'theta':m['Theta'].values[0],'implied Vol':m['impliedVolatility'].values[0]},index=[i])
                    option_position_report = option_position_report.append(tmp)
                    i+=1

        def get_delta_p(action,qty,delta):
            if action==TransactionActions.BUY:
                return qty*100*delta
            elif action==TransactionActions.SHORT_SELL:
                return -qty*100*delta

        dp = sum(np.vectorize(get_delta_p)(option_position_report['action'],option_position_report['qty'],option_position_report['delta']))
        portfolio_delta = sum(option_position_report['qty']*option_position_report['delta'])/sum(option_position_report['qty'])
        print("Your portfolio delta is: {}".format(portfolio_delta))
        outstanding_shares = round(self.get_total_securities_holdings() + dp,2)
        if outstanding_shares > 0:
            print("You are LONG {} shares, consider hedging".format(outstanding_shares))
        elif outstanding_shares < 0:
            print("You are SHORT {} shares, consider hedging".format(outstanding_shares))
        else:
            print("nice hedging!")

        print(option_position_report)

    def get_tkr_vwap(self, tkr):
        tkr_sec_data = self.get_all_securities_by_tkr(tkr)
        buys = tkr_sec_data.loc[tkr_sec_data['action']
                                == TransactionActions.BUY]
        sells = tkr_sec_data.loc[tkr_sec_data['action']
                                 == TransactionActions.SELL]

        buys_x_volume = (buys['price']*buys['qty']).sum()
        buy_volume = buys['qty'].sum()
        buy_vwap = buys_x_volume/buy_volume if buy_volume > 0 else nan

        sells_x_volume = (sells['price']*sells['qty']).sum()
        sell_volume = sells['qty'].sum()
        sell_vwap = sells_x_volume/sell_volume if sell_volume > 0 else nan
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
