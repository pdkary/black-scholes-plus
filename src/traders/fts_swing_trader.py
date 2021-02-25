import sys
tickers = ['AAPL', 'AMD', 'AMZN', 'CSCO', 'FB', 'GOOG','IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']
frequency = 120

from src.traders.swing_trader import MovingAverageService

MAService = MovingAverageService(tickers,period="6mo")

### ----------------------------- Weird FTS provided steup ------------------------------##
nArg=int(sys.argv[1])

i=1
bid=dict()
ask=dict()
last=dict()
qty=dict()
for tkr in tickers:
	i=i+1
	bid[tkr]=float(sys.argv[i])
	i=i+1
	ask[tkr]=float(sys.argv[i])
	i=i+1
	last[tkr]=float(sys.argv[i])
	qty[tkr]=list()
	for j in range(nArg):
		i=i+1
		qty[tkr].append(float(sys.argv[i]))
# the following 'constant' declarations refer to the different parts of qty for nArgs=7 (the current implementation)
cCashQty=0
cMarginQty=1
cShortQty=2
cCashAvailable=3
cCVAP=4
cTransCost=5
### ------------------------- End Weird FTS provided steup ------------------------------##
returnStr = dict()
for tkr in tickers:
    tkr_Str = MAService.get_action(tkr,bid[tkr],ask[tkr],qty[tkr][cCashQty],qty[tkr][cCashAvailable],qty[tkr][cCVAP])
    returnStr.update(tkr_Str)

print(returnStr)