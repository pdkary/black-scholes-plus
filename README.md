# Black-Scholes +
Black–Scholes model for equity derivatives + corresponding option data.

Py Script designed to efficiently employ BSM formula via automatically calculating the annualized standard deviation of the underlying in addition to the spot price, time to expiry, dividend yield, and the risk-free rate for option prices while also printing the corresponding option chain and related info (i.e. implied volatility, bid/ask, open interest, etc.).

## Installation
Script requires a few things, like yfinance for data, numpy for calculations, yada yada yada.
```python
    pip3 install -r requirements.txt
```

## Example Usage
Using the calculator is relatively simple, all you need to begin is a set of tickers, with corresponding strike prices to query.
```python
tickers = ['AAPL', 'GOOG', 'NVDA']
strike_map = {'AAPL':200,'GOOG':1220,'NVDA':650}

bsmc = BSM_Calculator(tickers,interval='1d')
```
This initializes the calculator, and requests 3 months of spot data, with `1d` (one day) between datapoints.
```python
rfr = 0.012 #risk free rate
dyield = 0 #dividend yield

bmsc_data = bsmc.get_report("2021-03-19",strike_map,rfr,dyield)
print(bsmc_data)
```
This queries yfinance's option api for options with matching strike price, and expiration date.  (expiration date may throw errors if no options are available).

It then generates a dataframe report of matching options, with their Black-Scholes value added as a column.
####Output:
```
[*********************100%***********************]  3 of 3 completed
  contractSymbol  type  strike  BSM Value  lastPrice     bid     ask  openInterest  impliedVolatility  Annual Volatility
0           AAPL  CALL   200.0       0.00       0.08    0.08    0.09       21714.0             0.5508             0.2916
1           AAPL   PUT   200.0      64.83      65.90   64.55   64.80         709.0             0.5137             0.2916
2           GOOG  CALL  1220.0     882.87     544.00  609.30  617.40           4.0             0.0000             0.2805
3           GOOG   PUT  1220.0       0.00       0.35    0.00    0.85          39.0             0.6868             0.2805
4           NVDA  CALL   650.0       6.33      18.85   18.55   19.25        2668.0             0.5274             0.3293
5           NVDA   PUT   650.0      58.54      64.47   68.50   71.45          42.0             0.5202             0.3293
```
##Modules
###Spot Data Service
Gathers market values for a set of securities, looking back over a given period, at a given interval.

Used for requesting data, and performing mathematical operations.

###Option Data Service
Gathers market values for put and call options on securities, expiring on a given date, with specified strike prices for each ticker.

Currently used only for requesting and formatting yfinance data.

###BSM_Calculator
This calculator uses the spot data service, to perform a vectorized black-scholes calculation on arrays of stock data.

get_report uses the option data service to query and display recent prices for options that meet the specified criteria, with their corresponding bsm value