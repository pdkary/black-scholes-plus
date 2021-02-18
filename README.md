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
Using the calculator is relatively simple, all you need to begin is a set of tickers, with corresponding strike prices to query.
```python
tickers = ['AAPL', 'GOOG', 'NVDA']
strike_map = {'AAPL':200,'GOOG':1220,'NVDA':650}

expr_date = "2021-02-19"
rfr = 0.012 #risk free rate

#Get report using specified strikes
rg = ReportGenerator(tickers,rfr)
report = rg.get_report(expr_date,strike_map)
```
This queries the last 1 year of daily price changes for each stock, and uses these to calculate standard deviation of 1 day changes.

Black-Scholes calculations are then done using the specified strike prices, and risk free rate.

Reports of recent matching options, are then shown, with their corresponding BSM value.
#### Output:
```
  contractSymbol  type  strike  BSM Value  lastPrice     bid     ask  impliedVolatility  Annual Vol
0           AAPL  CALL   200.0       0.00       0.01    0.00    0.01             1.8125      0.4705
1           AAPL   PUT   200.0      69.17      64.83   68.80   69.90             2.6875      0.4705
2           GOOG  CALL  1220.0     908.27     647.50  904.00  914.00             2.9941      0.3958
3           GOOG   PUT  1220.0       0.00       0.22    0.00    1.40             3.0000      0.3958
4           NVDA  CALL   650.0       0.01       0.24    0.24    0.28             0.5957      0.5839
5           NVDA   PUT   650.0      53.79      55.23   52.45   55.75             0.6231      0.5839
```

If instead, you wanted to use at-the-money prices
```python
report = rg.get_ATM_report(expr_date)
```
## Modules
### Spot Data Service
Gathers market values for a set of securities, looking back over a given period, at a given interval.

Used for requesting data, and performing mathematical operations.

### Option Data Service
Gathers market values for put and call options on securities, expiring on a given date, with specified strike prices for each ticker.

Currently used only for requesting and formatting yfinance data.

### BSM_Calculator
This calculator uses the spot data service, to perform a vectorized black-scholes calculation on arrays of stock data.

### Report Generator
Uses all previous modules to generate and display a report of recent calls, with BSM values, and implied/annual volatility