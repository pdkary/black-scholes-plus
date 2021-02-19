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

expr_date = "2021-02-19"
rfr = 0.012 #risk free rate

#Initialize Report generator with tickers and rfr
rg = ReportGenerator(tickers,rfr)
#Generate report
report = rg.get_ATM_report(expr_date)
print(report)
```
This queries the last 1 year of daily price changes for each stock, and uses these to calculate standard deviation of 1 day changes.

Black-Scholes calculations are then done using the specified strike prices, and risk free rate.

Reports of recent matching options, are then shown, with their corresponding BSM value.
#### Output:
```
  contractSymbol  type    spot  strike  BSM Value  lastPrice   bid   ask  openInterest  impliedVolatility  Annual Vol
0           AAPL  CALL  128.73   129.0       0.00       0.68  0.69  0.68          6361             0.2100      0.4699
1           AAPL   PUT  128.73   129.0       0.27       1.07  1.01  1.05         16721             0.2412      0.4699
2           NVDA  CALL  590.44   590.0       0.44       4.96  4.80  5.10          3530             0.2831      0.5829
3           NVDA   PUT  590.44   590.0       0.00       5.25  5.00  5.40          2659             0.3192      0.5829
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