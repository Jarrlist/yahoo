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

# Run parameters
filename = 'companies.txt'
runBlackList = False
debug = False


companies = fileHandeler.load(filename, runBlackList)

data = np.zeros((len(companies), 2))
beta = np.zeros(len(companies))
var = np.zeros(len(companies))
color = np.zeros(len(companies))
DCFSucess = np.zeros(len(companies))
fscore = np.zeros(len(companies))
marker = []
name = []
i = 0
for i, company in enumerate(companies):
    
    msft = yf.Ticker(company)
    try:
        print(colored("=============>  ", 'magenta') + str(msft.info['website'][11:-3]) + "(" + company + ")" + colored(" <=====  ", 'magenta'))
        name.append(str(msft.info['website'][11:-3])) 
    except: 
        print("=============  " + company + " ===============")
        name.append(company) 
    try:
        beta[i] = msft.info['beta']
        if (math.isnan(beta[i])):
            beta[i] = 1
    except: 
        beta[i] = 1
    gro, var[i], growthSuccess = help.growth(msft.financials.loc['Total Revenue'])

    if(gro < 0):    
        print("Revenue Growth: " + colored(str(round(100*gro, 2 )) + "%  ", 'red'))
    elif(gro < 0.05):
        print("Revenue Growth: " + colored(str(round(100*gro, 2 )) + "%", 'blue'))
    else:
        print("Revenue Growth: " + colored(str(round(100*gro, 2 )) + "% ", 'green') + emoji.emojize(':rocket:'))
    fscore[i], markerTemp =  help.Fscore(msft)
    marker.append(markerTemp)
    color[i] = help.PE(msft)
    #method1.evaluate(msft)
    data[i], DCFSucess[i] = dcf.intrinsic(msft, debug)

area = np.log10((np.power(beta,10) + np.power(var,10) )*10000)
area[area < 1] = 1
area*=40

# Filtering
filteredData = data[np.logical_and(DCFSucess == 1, color < 100)]
filteredColor = color[np.logical_and(DCFSucess == 1, color < 100)]
filteredArea = area[np.logical_and(DCFSucess == 1, color < 100)]
filteredScore = fscore[np.logical_and(DCFSucess == 1, color < 100)]
filteredMarker = []
filteredName = []
filteredCompanies = []
blacklistedCompanies = []

for i, n in enumerate(name):
    if(DCFSucess[i] and (color[i] < 100)):
        filteredName.append(n)
        filteredMarker.append(marker[i])
        filteredCompanies.append(companies[i])
    else:
        blacklistedCompanies.append(companies[i])

fileHandeler.save(filename, companies, blacklistedCompanies)

fig, ax = plt.subplots()
sc = ax.scatter(np.asarray(filteredData[:,0]), 100*np.asarray(filteredData[:,1]), 
        c=filteredColor, s=filteredArea, alpha=0.3, cmap='jet')
plt.title("DCF, assuming 10'%' annual return, year 1-5: current growth, 6-10: current growth/2 ")
plt.xlabel("Cheap To Expensive (1 = Fair Value)")
plt.ylabel("Growth In Percent")
plt.vlines(1, -10, 50, color="red")
plt.hlines(0, 0, 3, color="red")
for i, txt in enumerate(filteredName):
    ax.annotate(filteredCompanies[i].partition(".")[0] , (np.asarray(filteredData[i,0]), 100*np.asarray(filteredData[i,1]) +0.5), ha='center' )
    ax.annotate(str(round(filteredScore[i])), (np.asarray(filteredData[i,0]), 100*np.asarray(filteredData[i,1]) ), ha='center', va='center')
cbar = fig.colorbar(sc, ax=ax, orientation="vertical")
cbar.ax.set_xlabel('P/E - Ratio')
plt.show()
