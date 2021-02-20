from src.report_generator import ReportGenerator
import time
from datetime import date
from matplotlib import pyplot as plt
import numpy as np

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
    for i in range(1,len(tickers)+1):
        tkrs = tickers[0:i]
        print("starting test with: {}".format(tkrs))
        (duration,num_options,num_tkrs) = test(tkrs)
        print("test completed with: ({},{},{})".format(duration,num_options,num_tkrs))
        y.append(duration)
        x1.append(num_tkrs)
        x2.append(num_options)
    

    second_degree_yx1 = np.polyfit(x1,y,2)
    second_degree_yx2 = np.polyfit(x2,y,2)
    x1_label = "y(#tkrs) = {}x^2+{}x+{}".format(round(second_degree_yx1[0],2),round(second_degree_yx1[1],2),round(second_degree_yx1[2],2))
    x2_label = "y(#opts) = {}x^2+{}x+{}".format(round(second_degree_yx2[0],2),round(second_degree_yx2[1],2),round(second_degree_yx2[2],2))
    x1_func = np.vectorize(lambda x: second_degree_yx1[0]*(x**2) + second_degree_yx1[1]*x+second_degree_yx1[2])
    x2_func = np.vectorize(lambda x: second_degree_yx2[0]*(x**2) + second_degree_yx2[1]*x+second_degree_yx2[2])

    fig,axs = plt.subplots(1,2,figsize=(7,4))
    x1_range = max(x1)-min(x1)
    x2_range = max(x2)-min(x2)
    x1_axis = np.array([i/20 for i in range(min(x1),20*max(x1))])
    x2_axis = np.array([i/20 for i in range(min(x2),20*max(x2))])

    axs[0].plot(x1,y)
    axs[0].set_title("Number of tickers vs duration")
    axs[0].plot(x1_axis,x1_func(x1_axis))
    axs[0].set_xlabel(x1_label)

    axs[1].plot(x2,y)
    axs[1].set_title("Number of options vs duration")
    axs[1].plot(x2_axis,x2_func(x2_axis))
    axs[1].set_xlabel(x2_label)

    plt.savefig("reports/test_report.png")
    plt.close()


    