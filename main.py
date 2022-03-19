import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
from termcolor import colored
import emoji
import math
import PySimpleGUI as sg

import dcf
import help
import fileHandeler
import run

# Run parameters
filename = 'companies.txt'
runBlackList = False
debug = False

file_list_column = [
    [
        sg.Text("Run Stock: "),
        sg.In(size=(10, 1), enable_events=True, key="-TICKET-"),
        sg.Checkbox('Add to defualt:', default=True, key="-ADD-"),
        sg.Button("GO", key="-GO_TICKET-"),
    ],
    [
        sg.Text("Run File: "),
        sg.In(size=(50, 1), enable_events=True, key="-FILE-"),
        sg.FileBrowse(),
        sg.Checkbox('Run Blacklist:', default=False, key="-BLACKLIST_1-"),
        sg.Button("GO", key="-GO_FILE-"),
    ],
    [
        sg.Text("Run Defualt File: "),
        sg.Checkbox('Run Blacklist:', default=False, key="-BLACKLIST_2-"),
        sg.Button("GO", key="-GO_DEFUALT-"), 
    ],

]

layout = [
    [
        sg.Column(file_list_column),
    ]
]

window = sg.Window("Jarrlist's DCF Calculator", layout)

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "-GO_TICKET-":
        run.runCompany(values["-TICKET-"], single=values["-ADD-"])
    elif event == "-GO_FILE-":
        run.runFile(values["-FILE-"], values["-BLACKLIST_1-"])
    elif event == "-GO_DEFUALT-":
        run.runFile(filename, values["-BLACKLIST_2-"])
