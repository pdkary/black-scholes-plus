from datetime import datetime
from src.report_generator import ReportGenerator

class FTSTrader:
    @staticmethod
    def create_call_bear_spread(tkr,expr,strike_low,strike_high,quantity):
        returnString = dict()
        key_low = FTSTrader.get_fts_option_key(tkr,'CALL',expr,strike_low)
        key_high = FTSTrader.get_fts_option_key(tkr,'CALL',expr,strike_high)
        returnString[key_high] = 'shortsale/'+ str(quantity)
        returnString[key_low] = 'cashbuy/'+str(quantity)
        return returnString
    
    @staticmethod
    def create_call_bull_spread(tkr,expr,strike_low,strike_high,quantity):
        returnString = dict()
        key_low = FTSTrader.get_fts_option_key(tkr,'CALL',expr,strike_low)
        key_high = FTSTrader.get_fts_option_key(tkr,'CALL',expr,strike_high)
        returnString[key_high] = 'cashbuy/' + str(quantity)
        returnString[key_low] = 'shortsale/'+str(quantity)
        return returnString
    
    @staticmethod
    def create_put_bear_spread(tkr,expr,strike_low,strike_high,quantity):
        returnString = dict()
        key_low = FTSTrader.get_fts_option_key(tkr,'PUT',expr,strike_low)
        key_high = FTSTrader.get_fts_option_key(tkr,'PUT',expr,strike_high)
        returnString[key_high] = 'cashbuy/' + str(quantity)
        returnString[key_low] = 'shortsale/'+str(quantity)
        return returnString
    
    @staticmethod
    def create_put_bull_spread(tkr,expr,strike_low,strike_high,quantity):
        returnString = dict()
        key_low = FTSTrader.get_fts_option_key(tkr,'PUT',expr,strike_low)
        key_high = FTSTrader.get_fts_option_key(tkr,'PUT',expr,strike_high)
        returnString[key_high] = 'shortsale/' + str(quantity)
        returnString[key_low] = 'cashbuy/'+str(quantity)
        return returnString
    
    @staticmethod
    def create_iron_condor(tkr,expr,call_low,call_high,put_low,put_high,quantity):
        returnStr = dict()
        bear_call_spread = FTSTrader.create_call_bear_spread(tkr,expr,call_low,call_high,quantity)
        bull_put_spread = FTSTrader.create_put_bull_spread(tkr,expr,put_low,put_high,quantity)
        returnStr.update(bear_call_spread)
        returnStr.update(bull_put_spread)
        return returnStr

    @staticmethod
    def get_fts_option_key(tkr,type,expr,strike):
        type_id = "D" if type=="CALL" else "P"
        expr_date = datetime.strptime(expr_date,"%Y-%m-%d")
        yr = str(datetime.year())[2:]
        strike_str = str(strike)
        if strike < 100:
            strike_str = "0"+strike_str
        if strike < 1000:
            strike_str = strike_str + "00"
        if strike > 1000:
            strike_str = strike_str+"0"
        return tkr+type_id+expr_date.day()+strike_str