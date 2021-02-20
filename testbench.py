from src.report_generator import ReportGenerator
import time
from datetime import date
from matplotlib import pyplot as plt

tickers = ['AAPL', 'AMD', 'AMGN', 'AMZN', 'CSCO', 'FB','GOOG', 'IBM', 'INTC', 'MSFT', 'MU', 'NFLX', 'NVDA', 'SHOP']
rfr = 0.012

def test(tkrs):
    tic = time.perf_counter()
    rg = ReportGenerator(tkrs,rfr)
    report_atm = rg.get_ATM_multi_report()
    toc = time.perf_counter()
    return (toc-tic,len(report_atm.index),len(tkrs))

y = []
x1 = []
x2 = []
if __name__ == '__main__':
    for i in range(1,len(tickers)):
        tkrs = tickers[0:i]
        print("starting test with: {}".format(tkrs))
        (duration,num_options,num_tkrs) = test(tkrs)
        print("test completed with: ({},{},{})".format(duration,num_options,num_tkrs))
        y.append(duration)
        x1.append(num_tkrs)
        x2.append(num_options)
    
    fig,axs = plt.subplots(1,2,figsize=(7,3))
    axs[0].plot(x1,y)
    axs[0].set_title("Number of tickers vs duration")

    axs[1].plot(x2,y)
    axs[1].set_title("Number of options vs duration")
    plt.savefig("reports/test_report.png")
    plt.close()


    