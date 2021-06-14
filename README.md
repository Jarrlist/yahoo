The program takes down data from yahoo finance and performs DCF. 
The result is then printed in the terminal and illustrated if a file is choosen. 

To run the program:

1: Install python and all packages required, pip install -r requirements.txt

2: To run program type: "python main.py" in cmd or equivalent 

3: The GUI will be displayed. 

3.1: Run a single company by entering the yahoo ticket in the "run stock" field, then press "GO". 
The valuation will then be displayed in terminal. 

3.2: Run multiple companies by running a file. The file should be in .txt format and contain tickets 
separated with row breaks. select the file using "Browse" and hit "GO" to run the file. When 
all companies are valuated, a plot will display them. 

3.3: The defualt file is "companies.txt", to run this file hit "GO" on the third row. 
The file "companies.txt" can be modified, and the choice of defualt file can easily 
be changed in the main script "main.py".


Blacklist: When running files, tickets with unaviable values, or very bad valuations, will be removed from the file and added to the corrensponding blacklist (*-blacklist.txt). This is to save time when the file is run again at a later time. If one wants to give some of the companies in the blacklist a second chance, tick the "run blacklist" box and it will be included in the next run.  



Known issues and future improvments

1. Sometimes Corperate overhead margin is negative, I don't think that should be possible. 

2. Sometimes companies are filtered away for possibly minor reasons. 

3. Terminal value should be based on the industry of the company, for now it is not. This kind of data is unfortunally unaviable using the yahoo finance API. But it should be easy to calculate, so hopfully this script will calculate avarages for different industries and save it somehow in the future.

4. The files for the project should be organized better as the project gets bigger.  

5. GUI improvments, maybe pictures and printed values can be integrated into the GUI. 

6. There should be more files to run, maybe for different industries etc. If files could be generated automatically somehow, that would be nice aswell. 

7. Often one dose not want to run the full script again, just to see a picture. This is time consuming and annoying since Yahoo has very slow calls. Maybe data can be saved localy, and if data is aviable from the current day, used the saved data instead of getting it from yahoo. This would be lightning fast. 

8. More advanced methods for forcasting growth and margins. For now it is just avarages from recent years. 

9. Maybe factor in divedens, and it's date, in a more usefull way.    



If you are interested in helping out in this project, or if you have found bugs, contact me! Jarrlist@gmail.com
