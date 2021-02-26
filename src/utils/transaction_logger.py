import pandas as pd


class TransactionTypes:
    SECURITY = "security"
    PUT = "put"
    CALL = "call"


class TransactionActions:
    BUY = "cashbuy"
    SELL = "cashsale"
    SHORT_SELL = "shortsale"
    SHORT_COVER = "shortcover"


class TranactionLogger:
    cols = ["symbol", "time", "type", "expiration",
            "action", "price", "strike", "qty"]

    def __init__(self, filename=None):
        if filename is not None:
            self.load_from_csv(filename)
        else:
            self.data = pd.DataFrame(columns=self.cols)

    def load_from_csv(self, filename):
        self.data = pd.read_csv(filename)
        self.data = self.data[self.cols]

    def write_to_csv(self, filename):
        self.data.to_csv(filename)

    def add_transaction(self, tkr, trx_time, trx_type, expiration, action, price, strike, qty):
        raw_data = {"symbol": tkr, "time": trx_time, "type": trx_type, "expiration": expiration,
                    "action": action, "price": price, "strike": strike, "qty": qty}
        s = pd.DataFrame(raw_data, index=[len(self.data)])
        self.data = self.data.append(s)

    def buy_security(self, tkr, trx_time, price, qty):
        self.add_transaction(
            tkr, trx_time, TransactionTypes.SECURITY, None, TransactionActions.BUY, price, price, qty)

    def sell_security(self, tkr, trx_time, price, qty):
        self.add_transaction(
            tkr, trx_time, TransactionTypes.SECURITY, None, TransactionActions.SELL, price, price, qty)

    def short_security(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.SECURITY, None,
                             TransationActions.SHORT_SELL, price, price, qty)

    def cover_security(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.SECURITY, None,
                             TransactionActions.SHORT_COVER, price, price, qty)

    def buy_call(self, tkr, trx_time, expr, price, strike, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.CALL, expr,
                             TransactionActions.BUY, price, strike, qty)

    def sell_call(self, tkr, trx_time, expr, price, strike, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.CALL, expr,
                             TransactionActions.SELL, price, strike, qty)

    def short_call(self, tkr, trx_time, expr, price, strike, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.CALL, expr,
                             TransactionActions.SHORT_SELL, price, strike, qty)

    def cover_call(self, tkr, trx_time, expr, price, strike, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.CALL, expr,
                             TransactionActions.SHORT_COVER, price, strike, qty)

    def buy_put(self, tkr, trx_time, expr, price, strike, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.PUT, expr,
                             TransactionActions.BUY, price, strike, qty)

    def sell_put(self, tkr, trx_time, expr, price, strike, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.PUT, expr,
                             TransactionActions.SELL, price, strike, qty)

    def short_put(self, tkr, trx_time, expr, price, strike, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.PUT, expr,
                             TransactionActions.SHORT_SELL, price, strike, qty)

    def cover_put(self, tkr, trx_time, expr, price, strike, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.PUT, expr,
                             TransactionActions.SHORT_COVER, price, strike, qty)

    def get_all_securities_by_tkr(self, tkr):
        return self.data.loc[(self.data['symbol'] == tkr) & (self.data['type'] == TransactionTypes.SECURITY)]

    def get_all_options_by_tkr(self, tkr):
        return self.data.loc[(self.data['symbol'] == tkr) & (self.data['type'] != TransactionTypes.SECURITY)]
    
    def get_total_securities_holdings(self):
        prices = self.data.loc[(self.data['type']==TransactionTypes.SECURITY)]['price']
        qty = self.data.loc[(self.data['type']==TransactionTypes.SECURITY)]['qty']
        return sum(prices*qty)

    def get_all_tkrs(self):
        return list(set(self.data['symbol']))

    def get_all_sec_tkrs(self):
        return list(set(self.data.loc[self.data['type'] == TransactionTypes.SECURITY]['symbol']))

    def get_all_opt_tkrs(self):
        return list(set(self.data.loc[(self.data['type'] == TransactionTypes.PUT) | (self.data['type'] == TransactionTypes.CALL)]['symbol']))
