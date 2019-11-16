'''
Query the User for a stock ticker (e.g., "IBM")
Verify that the ticker is valid by returning the full name of the company (e.g., "IBM Corp." or other appropriate regulatory name) or query the User again
Query the User for Pertinent Year-Ended Dates (Program should check whether fiscal years are calendar years or otherwise and inform User ahead of time).  Example:  "Please enter Year-Ended Range (note: XYZ Corp. has a FYE 12/31):"  Start Date:  yyyy   End Date:  yyyy
Next, go through the appropriate financial statements (check appropriate filings, but 10K's are a good place to start) to collect data.  If data is missing, report why the program cannot be completed to the User and restart another query--but be sure that it is a valid denial.
Taking the financial data, prepare a professional Free Cash Flow Statement (as detailed as is possible or that you see fit, but at least including the following:  EBIT, NI, FCFF, FCFE, CCF).  Report these figures and also validate them by performing computations for FCFF, FCFE, and CCF using the alternate method (shown in class).
Offer to report these to a data file (preferably Excel)
Ask if another query is needed, or end program. Control flow.
FOR EXTRA CREDIT (10 points):  Validate the figures by scraping the data from google or yahoo and report these numbers as well as any variances.
'''
import edgar as e
import requests


def query_ticker():
    return input('Enter a ticker:')

def get_company_name(symbol):
    
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol) #yahoo internal site. https://beautifier.io/
    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']

# Given a ticker, looks in yahoo's db for query_ticker
def verify_ticker(ticker):

    # If ticker exists, Yahho returns company company_name, return True
    if get_company_name(ticker): # Yahoo returned company name
        return True
    # Yahoo returns None, return False
    else:
        print ('Invalid ticker')
        return False

def query_date_range():
    input("Please enter Year-Ended Range (note: XYZ Corp. has a FYE 12/31)\nStart Date: yyyy\nEnd Date:  yyyy")
    pass

def verify_date_range():
    pass

def collect_fin_statements():
    pass

def extract_fcf_data():
    pass

def export():
    pass

ticker = ""
while not verify_ticker(ticker): #while ticker not valid
    ticker = query_ticker()

query_date_range()
verify_date_range()
collect_fin_statements()
extract_fcf_data()
export()
