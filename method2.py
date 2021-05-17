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

def intrinsic(ticket, FFCF=False):
    years = 10
    discount = 0.1
    growthSlowDown = 2
    terminalValue = 15
    capital = help.totalCash(ticket)
    growth, _, growthSuccess = help.growth(ticket.financials.loc['Total Revenue'])
    if FFCF:
        fcf, fcfSuccess = help.FCF(ticket, True)
    else:
        fcfVal, fcfSuccess = help.FCF(ticket)
        fcf = fcfVal * np.ones(years)
        print("FCF: " + str(f'{round(fcf[0]):,}'))
    if(fcfSuccess==False or growthSuccess==False):
        return [0, 0], False
    else:
        futureFCF = fcf[0]
        PV = np.zeros(years + 1)
        div = np.zeros(years)
        try:
            divYeild = (ticket.info['previousClose']*
                        ticket.info['trailingAnnualDividendYield']*
                        ticket.info['sharesOutstanding'])
            if(math.isnan(divYeild)):
                divYeild = 0
        except:
            divYeild = 0

        for i in range(years):
            if (FFCF):
                if (i < 5):
                    futureFCF = futureFCF*(1+3*growth/4) + fcf[i]/4   
                else:
                    futureFCF = futureFCF*(1+3*growth/(4*growthSlowDown)) + fcf[i]/(4*growthSlowDown)  
            else:
                if (i < 5):
                    futureFCF *= (1+growth) #fcf[i] + futureFCF*growth
                    divYeild *= (1 + growth)
                else:
                    futureFCF *= (1+growth/growthSlowDown)    #fcf[i] + futureFCF*growth/growthSlowDown
                    divYeild *= (1 + growth/growthSlowDown)
            div[i] = divYeild/(np.power(1 + discount, i + 1))
            PV[i] = futureFCF/(np.power(1 + discount, i + 1))

        PV[10] = terminalValue*PV[9]
        enterpriseValue = np.sum(PV) + capital #+ sum(div)
        try:
            stockInt, stockIntSucces = EVtoShare(ticket, enterpriseValue)
            current = ticket.info['open']
            if(math.isnan(stockInt) or math.isnan(current) or (not stockIntSucces)):
                print(colored("WARNING: COULD NOT find share price, using enterprise value instead", 'yellow' ))
                current = ticket.info['enterpriseValue']
                stockInt = enterpriseValue
        except:
            print(colored("WARNING: COULD NOT find SharesOutstanding, using enterprise value instead", 'yellow' ))
            stockInt = enterpriseValue
            try:
                current = ticket.info['enterpriseValue']
                if(math.isnan(current)):
                    print(colored("WARNING: COULD NOT CALCULATE FCF", 'yellow' ))
                    return [0, 0], False
            except:
                print(colored("WARNING: COULD NOT CALCULATE FCF", 'yellow' ))
                return [0, 0], False

        print("Instrinsic value: " + f'{np.round(stockInt,2):,}')  
        if(current > stockInt):
            print ("Current ask price: " + colored(f'{round(current,2):,}', 'red'))  
        else:
            print ("Current ask price: " + colored(f'{round(current,2):,}', 'green') + emoji.emojize('  :rocket: :rocket: :rocket:')) 
        
        if (stockInt < 0):
            print(colored("WARNING: Intrinsic value is negative", 'yellow' ))
            return  [current/stockInt, growth], False
        elif (current/stockInt > 4):
            print(colored("WARNING: Stock is silly overvalued and wont be graphed", 'yellow' ))
            return  [current/stockInt, growth], False
        else:
            return  [current/stockInt, growth], True


# Main version nu.. Funkar inte riktigt
def intrinsic2(ticket):
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

    print("grossMargin: " + f'{np.round(grossMargin,2):,}')
    print("corporateOverheadMargin: " + f'{np.round(corporateOverheadMargin,2):,}')
    print("EbitdaMargin: " + f'{np.round(EbitdaMargin,2):,}')
    print("interestToDebt: " + f'{np.round(interestToDebt,2):,}')
    print("capExMargin: " + f'{np.round(capExMargin,2):,}')
    print("DAratio: " + f'{np.round(DAratio,2):,}')
    print("wcMargin: " + f'{np.round(wcMargin,2):,}')
    print("taxMargin: " + f'{np.round(taxMargin,2):,}')
    print("UFCF: " + f'{np.round(FCF[0],2):,}')

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


