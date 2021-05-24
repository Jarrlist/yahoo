import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import numpy as np
import colorsys

blacklist = 'blacklistedCompanies.txt'

def load(filename, runBlackList=False):
    with open(filename) as f:
        companiesRead = f.read().splitlines()

    if (runBlackList):
        with open(blacklist) as f:
            blackCompaniesRead = f.read().splitlines()
        # Remove duplicates
        companies = list(dict.fromkeys(companiesRead + blackCompaniesRead))
    else:
        companies = list(dict.fromkeys(companiesRead))

    file = open(filename,"r+")
    file.truncate(0)
    file.close()
    # Write list of names without duplicates
    with open(filename, 'w') as filehandle:
        for listitem in companies:
            filehandle.write('%s\n' % listitem)
    return companies

def save(filename, companies, blacklistedCompanies):
    file = open(filename,"r+")
    file.truncate(0)
    file.close()
    with open(filename, 'w') as filehandle:
        for listitem in companies:
            filehandle.write('%s\n' % listitem)

    file = open(blacklist,"r+")
    file.truncate(0)
    file.close()
    with open(blacklist, 'w') as filehandle:
        for listitem in blacklistedCompanies:
            filehandle.write('%s\n' % listitem)

    # Remove duplicates in blacklist
    with open(blacklist) as f:
        companiesRead = f.read().splitlines()
    blacklistedCompanies = list(dict.fromkeys(companiesRead))
    file = open(blacklist,"r+")
    file.truncate(0)
    file.close()
    with open(blacklist, 'w') as filehandle:
        for listitem in blacklistedCompanies:
            filehandle.write('%s\n' % listitem)

    
    