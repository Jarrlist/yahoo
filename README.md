The program takes down data from yahoo finance and performs DCF. 
The result is then illustrated. 

To run the program:

1: Install python and all packages required, pip install -r requirements.txt

2: To run program type: python main.py

3: The GUI will be displayed. 

Run a single company by entering the yahoo ticket in the "run stock" field, then press "GO". 
The valuation will then be displayed in terminal. 

Run multiple companies by running a file. The file should be in .txt format and contain tickets 
separated with row breaks. select the file using "Browse" and hit "GO" to run the file. When 
all companies are valuated, a plot will display them. 

The defualt file is "companies.txt", to run this file hit "GO" on the third row. 
The file "companies.txt" can be modified, and the choice of defualt file can easily 
be changed in the main script "main.py".
The defualt file automatically removes companies with bad valuations or missing values every time
it runs. This is to save time. If one wants to give one or more of the companies in the blacklist 
a second go, tick the "run blacklist" checkbox and it will be included the next run. 
