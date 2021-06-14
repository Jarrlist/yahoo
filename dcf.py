import yfinance as yf
import numpy as np
import help
from termcolor import colored
import math
import emoji

def EVtoShare(ticket, EV):
    #EV = MC + Debt - Cash
    # MC = EV - Debt + Cash
    try:
        MC = EV - np.abs(ticket.balance_sheet.loc['Total Liab'][0]) 
        MC += help.totalCash(ticket)
        if(math.isnan(MC)):
            print(colored("WARNING: COULD NOT CALCULATE SHARE PRICE", 'yellow' ))
            return 0, False
    except:
        print(colored("WARNING: COULD NOT CALCULATE SHARE PRICE", 'yellow' ))
        return 0, False

    # shareprice = MC/shares outstanding
    try:
        share = MC/ticket.info['sharesOutstanding']
        if(math.isnan(share)):
            print(colored("WARNING: COULD NOT CALCULATE SHARE PRICE", 'yellow' ))
            return 0, False
    except:
        print(colored("WARNING: COULD NOT CALCULATE SHARE PRICE", 'yellow' ))
        return 0, False
    
    return share, True

# Main version nu.. Funkar inte riktigt
def intrinsic(ticket, debug=False):
    years = 10
    discout = 0.1
    price = help.getClose(ticket)
    outStanding = help.getOutstanding(ticket)
    MC = price*outStanding
    debt = help.getDebt(ticket)
    cash = help.totalCash(ticket)
    EV = MC + debt - cash

    revenue, _, growth = help.getRevenue(ticket)

    grossProfit, grossMargin = help.getGrossProfit(ticket)

    Ebitda, EbitdaMargin = help.getEBITDA(ticket)

    corporateOverhead = grossProfit - Ebitda
    corporateOverheadMargin = corporateOverhead/revenue

    interest, interestToDebt = help.getInterestCost(ticket, debt)

    capEx, capExMargin = help.getCapex(ticket)


    DAratio = help.getDAtoCapex(ticket)
    operationProfit = Ebitda - interest - DAratio*capEx
    operationProfitMargin = operationProfit/revenue

    tax, taxMargin = help.getTax(ticket)
    # net working capital senare
    cwc, wcMargin = help.getWorkingCapital(ticket)

    everything = (price + outStanding + debt + cash + revenue + growth 
                + grossProfit + grossMargin + Ebitda + EbitdaMargin 
                + interest + interestToDebt + capEx + capExMargin
                + DAratio + tax + taxMargin + cwc + wcMargin)
    if(math.isnan(everything)):
        print(colored("WARNING: SOME VALUE WAS NaN", 'yellow' ))
        return [0,0], False

    FCF = np.zeros(years)
    for i in range(years-1):
        rev = np.power(1+growth, i+1) * revenue
        gross = rev*grossMargin
        corp = rev*corporateOverheadMargin
        Eb = rev*EbitdaMargin
        interest = debt*interestToDebt
        cap = rev*capExMargin
        DA = DAratio*cap
        opProfit = Eb - interest - DA
        tax = (Eb - DA - interest)*taxMargin
        netInc = Eb-DA-interest-tax
        cwc = -cwc + rev*wcMargin
        #print(str(round(Eb)) + " ,  " + str(round(cap))+ " ,  " +  str(round(cwc)) + " ,  " + str(round(tax)))

        FCF[i] = (Eb - cap + cwc - tax)/np.power((1+discout), i+1)
    FCF[years-1] = FCF[-1]*(1+discout)/(discout-growth)/np.power((1+discout), years)
    
    FutureEnterprice = sum(FCF)
    futureEquity = FutureEnterprice - debt + cash
    targetSharePrice = futureEquity/outStanding

    if debug:
        for line in [["gross", "Overhead", "Ebitda", "interest", "CapEx", "DAratio", "wcMargin", "tax"], 
                        [f'{np.round(grossMargin,2):,}' , f'{np.round(corporateOverheadMargin,2):,}' , 
                f'{np.round(EbitdaMargin,2):,}' , f'{np.round((debt*interestToDebt)/revenue,2):,}'
                , f'{np.round(capExMargin,2):,}' , f'{np.round(DAratio,2):,}' 
                , f'{np.round(wcMargin,2):,}' , f'{np.round(taxMargin,2):,}']]:
            print('{:>0} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}'.format(*line))
        
    print("Instrinsic value: " + f'{np.round(targetSharePrice,2):,}')  
    if(price > targetSharePrice):
        print ("Current ask price: " + colored(f'{round(price,2):,}', 'red'))  
    else:
        print ("Current ask price: " + colored(f'{round(price,2):,}', 'green') + emoji.emojize('  :rocket: :rocket: :rocket:')) 

    if(targetSharePrice < 0):
        return [0, 0], False
    if(price/targetSharePrice > 5):
        return [(price/targetSharePrice), growth], False
    return [(price/targetSharePrice), growth], True 


