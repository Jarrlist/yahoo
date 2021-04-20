The program takes down data from yahoo finance and performs DCF. 
The result is then illustrated. 

To run the program:
1. Install python and all packages required
2. Add or remove companies from "conpanies.txt", must be in YahooFinance ticker form
3. main.py has a bool variable "runBlacklist", set this to False if you don't want to rerun companies with bad results or errors earlier. 
4. Run with python main.py

The program has some unreasonable results at the moment. Will hopefully be more robust in the future. 