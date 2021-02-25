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
    cols = ["symbol", "time", "type", "action", "price", "qty"]

    def __init__(self):
        self.data = pd.DataFrame(columns=self.cols)

    def add_transaction(self, tkr, trx_time, trx_type, action, price, qty):
        self.data.append(
            pd.Series([tkr, trx_time, trx_type, action, price, qty]))

    def buy_security(self, tkr, trx_time, price, qty):
        self.add_transaction(
            tkr, trx_time, TransactionTypes.SECURITY, TransactionActions.BUY, price, qty)

    def sell_security(self, tkr, trx_time, price, qty):
        self.add_transaction(
            tkr, trx_time, TransactionTypes.SECURITY, TransactionActions.SELL, price, qty)

    def short_security(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.SECURITY,
                             TransationActions.SHORT_SELL, price, qty)

    def cover_security(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.SECURITY,
                             TransactionActions.SHORT_COVER, price, qty)

    def buy_call(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.CALL,TransactionActions.BUY,price,qty)

    def sell_call(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.CALL,TransactionActions.SELL,price,qty)

    def short_call(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.CALL,TransactionActions.SHORT_SELL,price,qty)

    def cover_call(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.CALL,TransactionActions.SHORT_COVER,price,qty)

    def buy_put(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.PUT,TransactionActions.BUY,price,qty)

    def sell_put(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.PUT,TransactionActions.SELL,price,qty)

    def short_put(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.PUT,TransactionActions.SHORT_SELL,price,qty)

    def cover_put(self, tkr, trx_time, price, qty):
        self.add_transaction(tkr, trx_time, TransactionTypes.PUT,TransactionActions.SHORT_COVER,price,qty)
