from flask import Flask,request,jsonify,json
from flask_jsonpify import jsonpify
from src.report_generator import ReportGenerator

app = Flask(__name__)
tickers = []
rg = None
def dataframe_to_json(df):
    df_list = df.values.tolist()
    JSONP_data = jsonpify(df_list)
    return JSONP_data

class ReportTypes:
    ATM_SINGLE_EXPR = 1
    ATM_SHIFT_ABS_SINGLE_EXPR = 2
    ATM_SHIFT_REL_SINGLE_EXPR = 3
    ANY_SINGLE_EXPR = 4
    ATM_MULTI_EXPR = 5
    ATM_SHIFT_ABS_MULTI_EXPR = 6
    ATM_SHIFT_REL_MULTI_EXPR = 7
    ANY_MULTI_EXPR = 8

@app.route('/api/tickers',methods=['GET'])
def get_tickers():
    global tickers
    return jsonify({"tickers":tickers})

@app.route('/api/tickers',methods=['POST'])
def set_tickers():
    global rg
    global tickers
    content = request.get_json()
    tickers = content['tickers']
    rfr = content['risk-free-rate']
    rg = ReportGenerator(tickers,rfr)
    return jsonify({"new_tickers":rg.tickers})

@app.route('/api/bsm-data',methods=['POST'])
def request_bsm():
    global rg
    global tickers
    if len(tickers)==0:
        return jsonify({"error":"you must specify tickers first"})
    content = request.json
    req_type = content['request-type']
    if req_type < 5:
        expr_date = content['expiration']
        if req_type == ReportTypes.ATM_SINGLE_EXPR:
            df = rg.get_ATM_report(expr_date)
            return dataframe_to_json(df)
        if req_type == ReportTypes.ATM_SHIFT_ABS_SINGLE_EXPR:
            x = content['abs-shift']
            df = rg.get_ATM_plus_x(expr_date,x)
            return dataframe_to_json(df)
        if req_type == ReportTypes.ATM_SHIFT_REL_SINGLE_EXPR:
            x = content['rel-shift']
            df = rg.get_ATM_plus_x_percent(expr_date,x)
            return dataframe_to_json(df)
        if req_type == ReportTypes.ANY_SINGLE_EXPR:
            strike_map = content['strike-map']
            df = rg.get_report(expr_date,strike_map)
            return dataframe_to_json(df)
    else:
        expr_date_map = content['expiration-map']
        date_range = content['date-range']
        if req_type == ReportTypes.ATM_MULTI_EXPR:
            df = rg.get_ATM_multi_report(expr_date_map,date_range)
            return dataframe_to_json(df)
        if req_type == ReportTypes.ATM_SHIFT_ABS_MULTI_EXPR:
            x = content['abs-shift']
            df = rg.get_ATM_multi_report_plus_x(x,expr_date_map,date_range)
            return dataframe_to_json(df)
        if req_type == ReportTypes.ATM_SHIFT_REL_MULTI_EXPR:
            x = content['rel-shift']
            df = rg.get_ATM_multi_report_plus_x_percent(x,expr_date_map,date_range)
            return dataframe_to_json(df)
        if req_type == ReportTypes.ANY_MULTI_EXPR:
            strike_map = content['strike-map']
            df = rg.get_multi_expiration_report(strike_map,expr_date_map,date_range)
            return dataframe_to_json(df)
   
if __name__ == '__main__':
    app.run(host= '127.0.0.1',debug=True)