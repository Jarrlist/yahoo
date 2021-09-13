import yfinance as yf
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import math


def growth(ticket):
    try:
        arr = ticket.financials.loc['Total Revenue']
    except: 
        print (colored("WARNING, Cant get revenue", 'yellow'))
        return 0, 0, False

    if(math.isnan(np.sum(arr))): 
        print (colored("WARNING, growth input NAN, cant't calculate growth!", 'yellow'))
        return 0, 0, False

    if(len(arr) == 1): 
        print (colored("WARNING, No growth data", 'yellow'))
        return 0, 0, False

    growth = 0
    sum = 0
    for x in range(len(arr)-1):
        if(arr[x+1] == 0): 
            print (colored("WARNING, No growth data", 'yellow'))
            return 0, 0, False
        temp = (arr[x]/arr[x+1]) 
        if ((temp < 0.3) or temp > 2.5 ):
            print (colored("WARNING, CHANGE Growth!", 'yellow'))
        else:
            growth = growth + temp
            sum = sum + 1

    if(sum == 0): 
        print (colored("WARNING, No growth data", 'yellow'))
        return 0, 0, False
    avarageGrowth = growth/sum 
    return (avarageGrowth - 1), 0, True

def PE(ticket):
    try:
        pe = ticket.info['trailingPE']
        if(math.isnan(pe)):
            print (colored("WARNING, P/e NaN! calculating from financials", 'yellow'))
            price = ticket.info['open']*ticket.info['sharesOutstanding']
            earnings = ticket.Earnings.values[0]
            pe = price/earnings
    except:
        pe = 99
        print (colored("WARNING, Could not find p/e Setting it to 99", 'yellow'))

    if(math.isnan(pe) or pe == 0):
        pe = 99
        print (colored("WARNING, Could not find p/e Setting it to 99", 'yellow'))

    if(pe < 30):
        print("Trailing P/E: " + colored(str(round(pe,2)), 'green'))
    else: 
        print("Trailing P/E: " + colored(str(round(pe,2)), 'red'))
    return(pe)

def tts(ticket):
    # Omsättning / andelar = omsättning per aktie
    # Denna stämmer rätt bra med avanza, ibland kusligt bra
    shares = ticket.info['sharesOutstanding']
    revenue = ticket.quarterly_earnings.Revenue.values
    tts = np.sum(revenue/shares)
    return tts

def getClose(ticket):
    try:
        current = ticket.info['open']
    except:
        print (colored("WARNING, Open price unaviable", 'yellow'))
        return float("NaN")
    return current

def getOutstanding(ticket):
    try:
        outstanding = ticket.info['sharesOutstanding']
    except:
        print (colored("WARNING, outstanding unaviable", 'yellow'))
        return float("NaN")
    if (outstanding == 0):
        print (colored("WARNING, outstanding unaviable", 'yellow'))
        return float("NaN")

    return outstanding   

def getRevenue(ticket):
    try: 
        revenue = ticket.financials.loc['Total Revenue']
    except:
        print (colored("WARNING, Revenue could not be calculated", 'yellow'))
        return float("NaN"), float("NaN"), float("NaN")

    if(np.any(revenue == 0)):
        print (colored("WARNING, Revenue could not be calculated", 'yellow'))
        return float("NaN"), float("NaN"), float("NaN")
    gro,_,_ = growth(revenue)
    return revenue[0], revenue, gro

def getDebt(ticket): 
    try:
        totalLiab = ticket.balance_sheet.loc['Total Liab'][0]
        sharholderEqt = ticket.balance_sheet.loc['Total Stockholder Equity'][0]
        totalDebt = totalLiab - sharholderEqt
    except:
        print (colored("WARNING, Debt unaviable", 'yellow'))
        return float("NaN")

    if(totalLiab == 0):
        print (colored("WARNING, Debt unaviable", 'yellow'))
        return float("NaN")

    return totalDebt

def totalCash(ticket):
    try:
        cash = ticket.quarterly_balance_sheet.loc['Cash'][0]
        if(math.isnan(cash)):
            print (colored("WARNING, Cash unaviable", 'yellow'))
            cash = 0
    except:
        cash = 0
        print (colored("WARNING, Cash unaviable", 'yellow'))
        return float("NaN")
    try:
        short = ticket.quarterly_balance_sheet.loc["Short Term Investments"][0]
        if(math.isnan(short)):
            print (colored("WARNING, short term investments unaviable", 'yellow'))
            short = 0
    except:
        short = 0

    if(cash == 0):
        return float("NaN")
    
    return cash + short

def getEBITDA(ticket):
    # Tror amortization är fel
    try:
        netIncome = ticket.financials.loc['Net Income']
        intreset = np.abs(ticket.financials.loc['Interest Expense'])
        
        opProfit = ticket.financials.loc["Operating Income"]
        netIncome = ticket.financials.loc['Net Income']
        tax = np.abs(ticket.financials.loc['Income Tax Expense'])
        Da = np.abs((opProfit - netIncome - tax)/2)


    except:
        print (colored("WARNING, EBITDA not aviable, can not be calculated", 'yellow'))
        return float("NaN"), float("NaN")
    EBITDA = netIncome + intreset + tax + Da
    if(math.isnan(sum(EBITDA))):
        print (colored("WARNING, EBITDA contained NaN value, can not be calculated", 'yellow'))
        return float("NaN"), float("NaN")

    margin = sum(EBITDA/getRevenue(ticket)[1])/len(EBITDA)
    return EBITDA[0], margin

def getGrossProfit(ticket):
    try:
        grossProfit = ticket.financials.loc['Gross Profit']
    except:
        print (colored("WARNING, Gross Profit could not be calculated", 'yellow'))
        return float("NaN"), float("NaN")
    margin = sum(grossProfit/getRevenue(ticket)[1])/len(grossProfit)
    if (math.isnan(margin) or (math.isnan(sum(grossProfit)))):
        print (colored("WARNING, Gross Profit could not be calculated", 'yellow'))
        return float("NaN"), float("NaN")
    return grossProfit[0], margin

def getTax(ticket):
    try:
        tax = np.abs(ticket.financials.loc['Income Tax Expense'])
    except:
        print (colored("WARNING, Tax Expense could not be calculated", 'yellow'))
        return float("NaN"), float("NaN")
    margin = tax[0]/getEBITDA(ticket)[0]
    return tax[0], margin

def getInterestCost(ticket, debt=1):
    try:
        interest = np.abs(ticket.financials.loc['Interest Expense'])
    except:
        print (colored("WARNING, Interest could not be calculated", 'yellow'))
        return float("NaN"), float("NaN")
    margin = sum(interest)/len(interest)
    return interest[0], margin/debt

def getDAtoCapex(ticket):
    # Ny ide 
    # opProfit = Eb - interest - DA
    # Da = opProfit - Eb + interest
    # Eb = netIncome + intreset + tax + depreciation + amortization
    # 2*Da = opProfit - netIncome - tax
    try:
        capEx = np.abs(ticket.cashflow.loc["Capital Expenditures"])
        opProfit = ticket.financials.loc["Operating Income"]
        netIncome = ticket.financials.loc['Net Income']
        tax = np.abs(ticket.financials.loc['Income Tax Expense'])
        Da = np.abs((opProfit - netIncome - tax)/2)
        margin = np.abs(Da/(capEx + Da))
    except: 
        print (colored("WARNING, D&A could not be calculated (get)", 'yellow'))
        return float("NaN")
    if math.isnan(sum(margin)):
        print (colored("WARNING, D&A could not be calculated (NaN)", 'yellow'))
        return float("NaN")

    avgRatio = sum(margin)/len(margin)
    return avgRatio

def getCapex(ticket):
    # Läs getDAtoCapex ....
    try:
        capEx = np.abs(ticket.cashflow.loc["Capital Expenditures"])
        
        opProfit = ticket.financials.loc["Operating Income"]
        netIncome = ticket.financials.loc['Net Income']
        tax = np.abs(ticket.financials.loc['Income Tax Expense'])
        Da = np.abs((opProfit - netIncome - tax)/2)

    except:
        print (colored("WARNING, CapEx could not be calculated", 'yellow'))
        return float("NaN"), float("NaN")
    cap = capEx + Da
    margin = sum(cap/getRevenue(ticket)[1])/len(capEx)
    return capEx[0], margin

def getWorkingCapital(ticket):
    try:
        liab = ticket.balance_sheet.loc['Total Current Liabilities']
        asset = ticket.balance_sheet.loc['Total Current Assets']
    except:
        print (colored("WARNING, Working capital could not be calculated", 'yellow'))
        return float("NaN"), float("NaN")
    workingCapital = asset - liab
    margin = sum(workingCapital/getRevenue(ticket)[1])/len(workingCapital)
    return workingCapital[0], margin

def FCF(ticket, regression=False, years=10):
    try:
        OCF = ticket.cashflow.loc['Total Cash From Operating Activities']
        if(math.isnan(sum(OCF))):
            print(colored("WARNING: COULD NOT FIND OCF", 'yellow' ))
            return 0, False
    except:
        print(colored("WARNING: COULD NOT FIND OCF", 'yellow' ))
        return 0, False

    try:
        capEx = np.abs(ticket.cashflow.loc["Capital Expenditures"])
        if(math.isnan(sum(capEx))):
            print(colored("WARNING: COULD NOT FIND capEx", 'yellow' ))
            return 0, False
    except:
        print(colored("WARNING: COULD NOT FIND capEx", 'yellow' ))
        return 0, False
    if (not regression):
        return (OCF[0] - capEx[0]), True
    else:
        # Pure line fit to extream
        x = np.array(range(0, len(OCF)))
        y = np.array(OCF-capEx)
        k, _ = np.polyfit(x, y, 1)
        if k > 1.2:
            k = 1.2

        if k < -0.2:
            k = -0.2

        m = np.average(OCF - capEx)
        x = np.array(range(1, 11))
        FFCF = m + x*((20-x)/(20))*(k/2)
        return FFCF, True

def Fscore(ticket):
    # ROA
    score = 0
    try:
        ROA = ticket.financials.loc['Net Income'][0] / ticket.balance_sheet.loc['Total Current Assets'][0]
        if math.isnan(ROA):
            print(colored("WARNING: COULD NOT CALCULATED ROA", 'yellow' ))
            ROA = -1
    except:
        print(colored("WARNING: COULD NOT CALCULATED ROA", 'yellow' ))
        ROA = -1
    if(ROA>0):
        score += 1
    else:
        print(colored("ROA negative last year!", 'red'))
    # OCF
    try:
        OCF = FCF(ticket)[0] + np.abs(ticket.cashflow.loc["Capital Expenditures"][0])
        if math.isnan(OCF):
            OCF = -1
            print(colored("WARNING: COULD NOT CALCULATED OCF", 'yellow' ))
    except:
        OCF = -1
        print(colored("WARNING: COULD NOT CALCULATED OCF", 'yellow' ))
    if(OCF>0):
        score += 1
    else:
        print(colored("OCF negative last year!", 'red'))

    # Change in ROA
    try:
        CROA = (ticket.financials.loc['Net Income'][0]/ticket.balance_sheet.loc['Total Current Assets'][0] 
                - ticket.financials.loc['Net Income'][1]/ticket.balance_sheet.loc['Total Current Assets'][1])
        if math.isnan(CROA):
            CROA = -1
            print(colored("WARNING: COULD NOT CALCULATED C-ROA", 'yellow' ))
    except:
        CROA = -1
        print(colored("WARNING: COULD NOT CALCULATED C-ROA", 'yellow' ))
    if(CROA > 0):
        score += 1
    else:
        print(colored("ROA decreased last year!", 'red'))
    # ACC
    try:
        ACC = ((FCF(ticket)[0] + np.abs(ticket.cashflow.loc["Capital Expenditures"][0]))
                / ticket.balance_sheet.loc['Total Current Assets'][0])
        if((not math.isnan(ACC)) and (not math.isnan(ROA)) and (not (ROA == -1))):
            if(ACC > ROA):
                score += 1
            else:
                print(colored("ACC < ROA last year!", 'red'))
        else:
            print(colored("WARNING: COULD NOT CALCULATED ROA OR ACC", 'yellow' ))
    except:
        print(colored("WARNING: COULD NOT CALCULATED ROA OR ACC", 'yellow' ))

    # leverage etc
    # Long term
    try:
        levChange = (ticket.balance_sheet.loc['Total Liab'][0]/ticket.financials.loc['Net Income'][0] 
                    - ticket.balance_sheet.loc['Total Liab'][1]/ticket.financials.loc['Net Income'][1])
        if(math.isnan(levChange)):
            levChange = 1
            print(colored("WARNING: COULD NOT CALCULATED LEVERAGE CHANGE", 'yellow' ))
    except:
        levChange = 1
        print(colored("WARNING: COULD NOT CALCULATED LEVERAGE CHANGE", 'yellow' ))
    if(levChange < 0):
        score += 1
    else:
        print(colored("Leverage increased last year!", 'red'))

    # asset to liability
    try:
        ratioChange = (ticket.balance_sheet.loc['Total Current Assets'][0]/ticket.balance_sheet.loc['Total Liab'][0] 
                    - ticket.balance_sheet.loc['Total Current Assets'][1]/ticket.balance_sheet.loc['Total Liab'][1])
        if(math.isnan(ratioChange)):
            ratioChange = -1
            print(colored("WARNING: COULD NOT CALCULATED ASSET TO LIABILITY", 'yellow' ))
    except:
        ratioChange = -1
        print(colored("WARNING: COULD NOT CALCULATED ASSET TO LIABILITY", 'yellow' ))
    if(ratioChange > 0):
        score += 1
    else:
        print(colored("Asset to Liability decreased last year!", 'red'))

    # Issued stock
    try:
        issuedStock = ticket.cashflow.loc['Issuance Of Stock'][0]
        if(math.isnan(issuedStock) or (issuedStock > 0)):
            score += 1
        else:
            print(colored("New stock was issued last year!", 'red'))
    except:
        score += 1
        print(colored("WARNING: DID NOT FIND NEW STOCK ISSUING", 'yellow' ))
    # Margin increas
    try:
        grossMargin = (ticket.financials.loc['Total Revenue'][0]
        - ticket.financials.loc['Cost Of Revenue'][0] - ticket.financials.loc['Total Operating Expenses'][0]
        -(ticket.financials.loc['Total Revenue'][1] - ticket.financials.loc['Cost Of Revenue'][1]
        - ticket.financials.loc['Total Operating Expenses'][1]))
        if (math.isnan(grossMargin)):
            grossMargin = -1
            print(colored("WARNING: COULD NOT CALCULATE GROSS MARGIN CHANGE", 'yellow' ))
    except:
        grossMargin = -1
        print(colored("WARNING: COULD NOT CALCULATE GROSS MARGIN CHANGE", 'yellow' ))
    if(grossMargin > 0):
        score += 1
    else:
        print(colored("Gross margin decreased last year!", 'red'))

    # Change in Asset turnover ratio
    try:
        turnover = (2*ticket.financials.loc['Total Revenue'][0]/(ticket.balance_sheet.loc['Total Current Assets'][0]
            + ticket.balance_sheet.loc['Total Current Assets'][1]) 
            - 2*ticket.financials.loc['Total Revenue'][1]/(ticket.balance_sheet.loc['Total Current Assets'][1]
            + ticket.balance_sheet.loc['Total Current Assets'][2])) 
        if (math.isnan(turnover)):
            turnover = -1
            print(colored("WARNING: COULD NOT CALCULATE TURNOVER RATIO", 'yellow' ))
    except:
        turnover = -1
        print(colored("WARNING: COULD NOT CALCULATE TURNOVER RATIO", 'yellow' ))
    if(turnover > 0):
        score += 1
    else:
        print(colored("Turnover ratio of assets decreased last year!", 'red'))

    print("F-score: " + str(score))
    if score < 4:
        marker = "v"
    elif score < 8:
        marker = "o"
    else:
        marker = "^"
    return score, marker
