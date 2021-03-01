import requests
import pandas as pd 
uri = "http://127.0.0.1:5000"
set_tkr_uri = uri + "/api/tickers"
bsm_data_uri = uri + "/api/bsm-data"
display_cols = ['contractSymbol','expiration','type','spot','strike','BSM Value','BSM% over ask', 'lastPrice', 'bid', 'ask', 'B/E','d% for BE','openInterest','Delta','Gamma','Theta','Vega','Rho','impliedVolatility', 'Annual Vol']

def test_atm_single_expr(expr):
    data = {'request-type':1,'expiration':expr}
    req = requests.post(bsm_data_uri,json=data)
    req_json = req.json()
    df = pd.DataFrame(req_json,columns=display_cols)
    print(df)

def test_atm_shift_abs_single_expr(expr,x):
    data = {'request-type':2,'expiration':expr,'abs-shift':x}
    req = requests.post(bsm_data_uri,json=data)
    req_json = req.json()
    df = pd.DataFrame(req_json,columns=display_cols)
    print(df)

def test_atm_shift_rel_single_expr(expr,x):
    data = {'request-type':3,'expiration':expr,'rel-shift':x}
    req = requests.post(bsm_data_uri,json=data)
    req_json = req.json()
    df = pd.DataFrame(req_json,columns=display_cols)
    print(df)

def test_any_single_expr(expr,strike_map):
    data = {'request-type':4,'expiration':expr,'strike-map':strike_map}
    req = requests.post(bsm_data_uri,json=data)
    req_json = req.json()
    df = pd.DataFrame(req_json,columns=display_cols)
    print(df)

def test_atm_multi_expr(expiration_map=None,date_range=None):
    data = {'request-type':5,'expiration-map':expiration_map,'date-range':date_range}
    req = requests.post(bsm_data_uri,json=data)
    req_json = req.json()
    df = pd.DataFrame(req_json,columns=display_cols)
    print(df)

def test_atm_shift_abs_multi_expr(x,expiration_map=None,date_range=None):
    data = {'request-type':6,'expiration-map':expiration_map,'date-range':date_range,'abs-shift':x}
    req = requests.post(bsm_data_uri,json=data)
    req_json = req.json()
    df = pd.DataFrame(req_json,columns=display_cols)
    print(df)

def test_atm_shift_rel_multi_expr(x,expiration_map=None,date_range=None):
    data = {'request-type':7,'expiration-map':expiration_map,'date-range':date_range,'rel-shift':x}
    req = requests.post(bsm_data_uri,json=data)
    req_json = req.json()
    df = pd.DataFrame(req_json,columns=display_cols)
    print(df)

def test_any_multi_expr(strike_map,expiration_map=None,date_range=None):
    data = {'request-type':8,'expiration-map':expiration_map,'date-range':date_range,'strike-map':strike_map}
    req = requests.post(bsm_data_uri,json=data)
    req_json = req.json()
    df = pd.DataFrame(req_json,columns=display_cols)
    print(df)

tickers = ['AAPL', 'AMD']
rfr = .012
if __name__== "__main__":
    data = {"tickers":tickers,"risk-free-rate":rfr}
    req1 = requests.post(set_tkr_uri,json=data)
    exp_end = "2021-04-01"
    exp_start = "2021-03-01"
    test_atm_single_expr(exp_end)
    input()
    test_atm_shift_abs_single_expr(exp_end,10)
    input()
    test_atm_shift_rel_single_expr(exp_end,.05)
    input()
    test_any_single_expr(exp_end,{'AAPL':140,'AMD':100})
    input()
    test_atm_multi_expr(date_range=(exp_start,exp_end))
    input()
    test_atm_shift_abs_multi_expr(10,date_range=(exp_start,exp_end))
    input()
    test_atm_shift_rel_multi_expr(.05,date_range=(exp_start,exp_end))
    input()
    test_any_multi_expr({'AAPL':140,'AMD':100},date_range=(exp_start,exp_end))

