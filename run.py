import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import numpy as np
import colorsys
from termcolor import colored
import emoji
import math

import dcf
import help
import fileHandeler

class RunData:
    name = []
    beta = []
    var = []
    growthSuccess = []
    fscore = []
    fScoreMarker = []
    pe = []
    data = []
    DCFSuccess = []
    def __init__(self):
        pass

    def add(self, name, beta, var, growthSuccess, fscore, marker, pe, data, DCFSucess):
        self.name.append(name)
        self.beta.append(beta)
        self.var.append(var)
        self.growthSuccess.append(growthSuccess)
        self.fscore.append(fscore)
        self.fScoreMarker.append(marker)
        self.pe.append(pe)
        self.data.append(data)
        self.DCFSuccess.append(DCFSucess) 

def runCompany(tickerName, debug = True, single=False):
    msft = yf.Ticker(tickerName)
    try:
        print(colored("=============>  ", 'magenta') +
            str(msft.info['website'][11:-3]) + "(" + tickerName + ")" + colored(" <=====  ", 'magenta'))
        name = str(msft.info['website'][11:-3])
    except:
        print("=============  " + tickerName + " ===============")
        name = tickerName
    try:
        beta = msft.info['beta']
        if (math.isnan(beta)):
            beta = 1
    except:
        beta = 1
    try:
        gro, var, growthSuccess = help.growth(msft)
    except:
        return "NaN", 0, 0, False, 0, "NaN", 0, [0,0], False
    if(growthSuccess == False):
        return "NaN", 0, 0, False, 0, "NaN", 0, [0,0], False

    if(gro < 0):
        print("Revenue Growth: " + colored(str(round(100*gro, 2)) + "%  ", 'red'))
    elif(gro < 0.05):
        print("Revenue Growth: " + colored(str(round(100*gro, 2)) + "%", 'blue'))
    else:
        print("Revenue Growth: " + colored(str(round(100*gro, 2)) +
                                            "% ", 'green') + emoji.emojize(':rocket:'))

    fscore, markerTemp = help.Fscore(msft)
    marker = markerTemp
    pe = help.PE(msft)
    data, DCFSucess = dcf.intrinsic(msft, debug)

    if (DCFSucess and (single==True)):
        companies = fileHandeler.load('companies.txt', False)
        companies.append(tickerName)
        fileHandeler.save('companies.txt', companies, [])

    return name, beta, var, growthSuccess, fscore, marker, pe, data, DCFSucess

def runFile(filename, runBlacklist=False):
    companies = fileHandeler.load(filename, runBlacklist)

    info = RunData()
    for i, company in enumerate(companies):
        print ("(" + str(i+1) + "/" + str(len(companies)) + ")    "),
        info.add(*runCompany(company))

    # Filtering
    dcfMask = np.array(info.DCFSuccess, dtype=object) == 1
    peMask = np.array(info.pe, dtype=object) < 100
    mask = np.logical_and(dcfMask, peMask)
    
    filteredData = np.array(info.data, dtype=object)[mask,:]
    filteredColor = np.array(info.pe, dtype=object)[mask]
    filteredScore = np.array(info.fscore, dtype=object)[mask]
    filteredMarker = []
    filteredName = []
    filteredCompanies = []
    blacklistedCompanies = []

    for i, n in enumerate(info.name):
        if(mask[i]):
            filteredName.append(n)
            filteredMarker.append(info.fScoreMarker[i])
            filteredCompanies.append(companies[i])
        else:
            blacklistedCompanies.append(companies[i])
    fileHandeler.save(filename, companies, blacklistedCompanies)

    #area = np.log10((np.power(info.beta, 10) + np.power(info.var, 10))*10000)
    #area[area < 1] = 1
    #area *= 40

    #print(filteredData.shape)

    fig, ax = plt.subplots()
    sc = ax.scatter(np.asarray(filteredData[:, 0]), 100*np.asarray(filteredData[:, 1]),
                    c=filteredColor, alpha=0.3, cmap='jet')
    plt.title("DCF, assuming 10'%' annual return, year 1-5: current growth, 6-10: current growth/2 ")
    plt.xlabel("Cheap To Expensive (1 = Fair Value)")
    plt.ylabel("Growth In Percent")
    plt.vlines(1, -10, 50, color="red")
    plt.hlines(0, 0, 3, color="red")
    for i, txt in enumerate(filteredName):
        ax.annotate(filteredCompanies[i].partition(".")[0], (np.asarray(
            filteredData[i, 0]), 100*np.asarray(filteredData[i, 1]) + 0.5), ha='center')
        ax.annotate(str(round(filteredScore[i])), (np.asarray(
            filteredData[i, 0]), 100*np.asarray(filteredData[i, 1])), ha='center', va='center')
    cbar = fig.colorbar(sc, ax=ax, orientation="vertical")
    cbar.ax.set_xlabel('P/E - Ratio')
    plt.show()
