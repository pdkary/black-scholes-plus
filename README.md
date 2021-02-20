# Black-Scholes +
Black–Scholes model for equity derivatives + corresponding option data.

Py Script designed to efficiently employ BSM formula via automatically calculating the annualized standard deviation of the underlying in addition to the spot price, time to expiry, dividend yield, and the risk-free rate for option prices while also printing the corresponding option chain and related info (i.e. implied volatility, bid/ask, open interest, etc.).

## Installation
Script requires a few things, like yfinance for data, numpy for calculations, yada yada yada.
```sh
git clone https://github.com/pdkary/black-scholes-plus.git
```
```python
pip3 install -r requirements.txt
```

## Example Usage
The Report Generator, is the heart of the entire application. This module uses all other services to gather spot and option data for each ticker, and performs black-scholes calculations for each ticker/expiry/strike 

As of right now, there are 3 methods of querying data
### Specified Strikes
If you have strike prices in mind, you query data using a specified expiration date
```python3
tickers = ['AAPL', 'GOOG', 'NVDA']
strikes = {'AAPL':140,'GOOG':2200,'NVDA':610}
expr_date = "2021-09-17"
rg = ReportGenerator(tickers,0.012)
rg.get_report(expr_date,strikes).to_csv("outputfilename.csv")
```
If instead you wanted to query options at this strike for all available expiration dates
```python3
tickers = ['AAPL', 'GOOG', 'NVDA']
strikes = {'AAPL':140,'GOOG':2200,'NVDA':610}
rg = ReportGenerator(tickers,0.012)
rg.get_multi_expiration_report(strikes).to_csv("outputfilename.csv")
```
### At-The-Money Strikes
If instead you do not have strike prices in mind, you can query ATM strike prices for a given expiration date
```python3
tickers = ['AAPL', 'GOOG', 'NVDA']
expr_date = "2021-09-17"
rg = ReportGenerator(tickers,0.012)
rg.get_ATM_report(expr_date).to_csv("outputfilename.csv")
```
You can also perform the same operation against all possible expiration dates
```python3
tickers = ['AAPL', 'GOOG', 'NVDA']
rg = ReportGenerator(tickers,0.012)
rg.get_ATM_multi_report().to_csv("outputfilename.csv")
```

### At-The-Money Plus X
For calculation revolving around the ATM price, methods are included for adding relative and absolute increases/decreases to ATM price, at a given expiration date.
#### Absolute increase by $10, at specific expiry
```python3
tickers = ['AAPL', 'GOOG', 'NVDA']
expr_date = "2021-09-17"
rg = ReportGenerator(tickers,0.012)
rg.get_ATM_plus_x(expr_date,10).to_csv("outputfilename.csv")
```
#### Relative increase by 10%, at specific expiry
```python3
tickers = ['AAPL', 'GOOG', 'NVDA']
expr_date = "2021-09-17"
rg = ReportGenerator(tickers,0.012)
rg.get_ATM_plus_x_percent(expr_date,.10).to_csv("outputfilename.csv")
```
#### Absolute increase by $10, at all expiries
```python3
tickers = ['AAPL', 'GOOG', 'NVDA']
rg = ReportGenerator(tickers,0.012)
rg.get_ATM_multi_report_plus_x(10).to_csv("outputfilename.csv")
```
#### Relative increase by 10%, at all expiries
```python3
tickers = ['AAPL', 'GOOG', 'NVDA']
rg = ReportGenerator(tickers,0.012)
rg.get_ATM_multi_report_plus_x_percent(.10).to_csv("outputfilename.csv")
```
**Note**: all examples can be found in examples.py
## Modules
### Spot Data Service
Gathers market values for a set of securities, looking back over a given period, at a given interval.

Used for requesting data, and performing mathematical operations.

### Option Data Service
Gathers market values for put and call options on securities, expiring on a given date, with specified strike prices for each ticker.

Currently used only for requesting and formatting yfinance data.

### BSM_Calculator
This calculator uses the spot data service, to perform a vectorized black-scholes calculation on arrays of stock data. Calculations include BSM value for CALL/PUT, Greeks, Implied volatility.

### Report Generator
Uses all previous modules to generate and display a report of recent calls, with BSM values, and implied/annual volatility.