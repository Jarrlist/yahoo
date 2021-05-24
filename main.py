import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import numpy as np
import colorsys
from termcolor import colored
import emoji
import math
import PySimpleGUI as sg
import os.path

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
        sg.Button("GO", key="-GO_TICKET-"),
    ],
    [
        sg.Text("Run File: "),
        sg.In(size=(50, 1), enable_events=True, key="-FILE-"),
        sg.FileBrowse(),
        sg.Button("GO", key="-GO_FILE-"),
    ],
    [
        sg.Text("Run Defualt File: "),
        sg.Checkbox('Run Blacklist:', default=False, key="-BLACKLIST-"),
        sg.Button("GO", key="-GO_DEFUALT-"), 
    ],

]

layout = [
    [
        sg.Column(file_list_column),
    ]
]

window = sg.Window("Image Viewer", layout)

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "-GO_TICKET-":
        run.runCompany(values["-TICKET-"])
    elif event == "-GO_FILE-":
        run.runFile(values["-FILE-"])
    elif event == "-GO_DEFUALT-":
        run.runFile(filename, values["-BLACKLIST-"])
