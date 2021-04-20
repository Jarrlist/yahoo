import yfinance as yf
import numpy as np
import help
import math
from termcolor import colored

def intrinsic(ticket):
    years = 10
    wantedReturn = 0.15
    gro, _ = help.growth(ticket)
    print("Revenue Growth: " +  str(round(100*gro,2)) + "%")
    t = help.tts(ticket)
    pe = help.PE(ticket)

    futureCashFlow = t
    for _ in range(years - 1):
        futureCashFlow = futureCashFlow + futureCashFlow*gro
    
    futurValue = futureCashFlow*pe
    intrinsic = futurValue
    intrinsic = intrinsic/np.power(1+wantedReturn,years)
    return intrinsic

def evaluate(ticket):
    margin = 2
    intValue = intrinsic(ticket)/margin
    print("Intrinsic value: " + str(intValue))
    now = ticket.info['regularMarketOpen']
    fairness = 100*now/intValue
    if(100*now/intValue > 100):
        print("Valuation is: " + colored(str(round(fairness,2)), 'red') + '%' + " of expected fair value!")
    else:
        print("Valuation is: " + colored(str(round(fairness,2)), 'green') + '%' + " of expected fair value!")
    