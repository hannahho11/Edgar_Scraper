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
from lxml import html

def query_ticker():
    return input('Enter a ticker:')

# Given a ticker, looks in Yahoo's internal database for company name
def get_company_name(symbol):

    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol) #yahoo internal site. https://beautifier.io/
    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            company_name = x['name']
            return company_name

def verify_ticker(ticker):

    # If ticker exists, Yahoo returns company name
    if get_company_name(ticker):
        return True
    # Yahoo returns None, return False
    elif ticker != "":
        print ('Invalid ticker')
        return False

# Given a link, saves, converts to html, returns html
def get_request(href):
    page = requests.get(href)
    return html.fromstring(page.content)

# Convert ticker input to CIK
def get_CIK_from_ticker(ticker):
    tree = get_request("https://www.sec.gov/cgi-bin/browse-edgar?CIK=" + ticker)
    cik = tree.xpath('//*[@id="contentDiv"]/div[1]/div[3]/span/a/text()')[0].rsplit()[0]
    return cik #split on space to get integers

# Fetches url of desired filings given CIK
def _get_filings_url(self, filing_type="", prior_to="", ownership="include", no_of_entries=100):
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + get_CIK_from_ticker(ticker) + "&type=" + filing_type + "&dateb=" + prior_to + "&owner=" +  ownership + "&count=" + str(no_of_entries)
    return url

def get_all_filings(self, filing_type="", prior_to="", ownership="include", no_of_entries=100):
    url = self._get_filings_url(filing_type, prior_to, ownership, no_of_entries)
    page = requests.get(url)
    return html.fromstring(page.content)

def get_10Ks(self, no_of_documents=10000):
    tree = self.get_all_filings(filing_type="10-K")
    elems = tree.xpath('//*[@id="documentsbutton"]')[:no_of_documents]
    result = []
    for elem in elems:
        url = BASE_URL + elem.attrib["href"]
        content_page = get_request(url)
        table = content_page.find_class("tableFile")[0]
        last_row = table.getchildren()[-1]
        href = last_row.getchildren()[2].getchildren()[0].attrib["href"]
        href = BASE_URL + href
        doc = get_request(href)
        result.append(doc)
    return result


def check_fye():
    docs = get_10Ks(no_of_documents=1)
    pass

def query_date_range(ticker):
    print("Please enter Year-Ended Range (note:", get_company_name(ticker),"has a FYE 12/31)\nStart Date: yyyy\nEnd Date:  yyyy")
    start = input('Start year (yyyy):')
    end = input('End year (yyyy):')
    return start, end

def get_ipo_year(ticker):
    return 1994

def verify_date_range(start_year, end_year):
    if end > start:
        return False
    elif start < get_ipo_year(ticker):
        print ('Date range start year before company IPO year')
        return False
    elif end > 2019:
        print ('End year is in the future')
        return False
    else :
        return True

# Given company, start year, end year, return relevant list of company 10-K's
def collect_fin_statements(start_year, end_year):
    get_10Ks()
    pass

def extract_fcf_data():
    pass

# Given FCF data, writes to a csv
def export():
    pass

def another_query_needed(): #Add if user inputs invalid****************************
    query = input('Another query needed? y/n').lower()
    if query == 'y' or query == 'yes':
        return True
    else:
        return False

while True:
    # Control flow
    TICKER = ""
    while not verify_ticker(TICKER): #while ticker not valid
        TICKER = query_ticker()

    query_date_range(TICKER)
    cik = get_CIK_from_ticker(TICKER)

    START_YEAR = None
    END_YEAR = None
    while not verify_date_range(START_YEAR, END_YEAR): #while date range not valid
        START_YEAR, END_YEAR = query_date_range(TICKER)

    all_statements_between_years = collect_fin_statements(START_YEAR, END_YEAR)
    fcf = extract_fcf_data(all_statements_between_years)
    export(fcf)

    if not another_query_needed():
        exit
