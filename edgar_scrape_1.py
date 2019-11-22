'''
Query the User for a stock ticker (e.g., "IBM")
Verify that the ticker is valid by returning the full name of the company (e.g., "IBM Corp." or other appropriate regulatory name) or query the User again
Query the User for Pertinent Year-Ended Dates (Program should check whether fiscal years are calendar years or otherwise and inform User ahead of time).
Example:  "Please enter Year-Ended Range (note: XYZ Corp. has a FYE 12/31):"  Start Date:  yyyy   End Date:  yyyy
Next, go through the appropriate financial statements (check appropriate filings, but 10K's are a good place to start) to collect data.
 If data is missing, report why the program cannot be completed to the User and restart another query--but be sure that it is a valid denial.
Taking the financial data, prepare a professional Free Cash Flow Statement (as detailed as is possible or that you see fit, but at least including the following:
EBIT, NI, FCFF, FCFE, CCF).  Report these figures and also validate them by performing computations for FCFF, FCFE, and CCF using the alternate method
(shown in class).
Offer to report these to a data file (preferably Excel)
Ask if another query is needed, or end program. Control flow.
FOR EXTRA CREDIT (10 points):  Validate the figures by scraping the data from google or yahoo and report these numbers as well as any variances.
'''
import edgar as e
import requests
from lxml import html
import re
# from bs4 import BeautifulSoup

def query_ticker():
    return input('Enter a ticker:').upper()

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
def get_request(url):
    response = requests.get(url)
    return html.fromstring(response.content)

# Convert ticker input to CIK
def get_CIK_from_ticker(ticker):
    tree = get_request("https://www.sec.gov/cgi-bin/browse-edgar?CIK=" + ticker)
    cik = tree.xpath('//*[@id="contentDiv"]/div[1]/div[3]/span/a/text()')[0].rsplit()[0]
    return cik #split on space to get integers

# Gets index of all companies, all filings w/in specified years
def get_index_links(start_year, end_year):
    # Search through all quarters in year range for relevant document
    directories = []
    base_url = 'https://www.sec.gov/Archives/edgar/full-index/'
    links_with_quarterly_index = []

    for year in range(start_year, end_year+1):
        for quarter in range(1,5):
            url = base_url + str(year) + '/QTR' + str(quarter) + '/' #sitemap.quarterlyindex.xml not in all folders
            page = get_request(url)
            links_list = page.xpath('//*[@id="main-content"]/table/tr/td/a') #for DEBUG any html object: .text_content()

            # Filters for links leading to quarterly index of all filings
            for link in links_list:
                if re.findall('quarterlyindex\d', link.text_content()):
                    quarterly_index_url = url + link.xpath('./@href')[0]
                    links_with_quarterly_index.append(quarterly_index_url)
        # import IPython
        # IPython.embed()
        # exit
    return links_with_quarterly_index

# Gets 10-K's from all types of filings, all companies, all years
def get_10Ks(ticker, cik, start_year, end_year, document='10-K'):
    links_with_quarterly_index = get_index_links(start_year, end_year)
    for url in links_with_quarterly_index:
        page = get_request(url)
        all_comps_all_filings_links_list = page.xpath('url/loc')

    #Filter for target company
    company_all_filing_urls = []
    for element in all_comps_all_filings_links_list:
        # Filter using matching CIK

        print(cik, element.text_content())
        if re.findall(cik.lstrip('0'), element.text_content()):
            print ('MATCH')
            company_all_filing_urls.append(link.text_content())

    # Filter for filing type
    the_10Ks = []
    for url in company_all_filing_urls:
        page = get_request(url)
        if re.findall('10-K', page.text_content()):
            the_10Ks.append(page)

    import IPython
    IPython.embed()
    exit
    #for each link, make a request and look for matching cik AND 10-K
    return the_10Ks

def get_fye(cik):
    # docs = get_10Ks(no_of_documents=1)
    return str(1111)

def query_date_range(ticker, cik):
    print("Please enter Year-Ended Range (note:", get_company_name(ticker),"has a FYE", get_fye(cik))
    while True:
        try:
            start = int(input('Start year (yyyy):'))
            end = int(input('End year (yyyy):'))
            break
        except:
            print ('Invalid start year')
    return start, end

def get_ipo_year(ticker):
    return 1994

def verify_date_range(start_year, end_year, ticker):
    if start_year is None or end_year is None:
        return False
    elif end_year < start_year:
        print ('end_year < start_year')
        return False
    elif start_year < get_ipo_year(ticker):
        print ('Date range start year before company IPO year')
        return False
    elif end_year > 2019:
        print ('End year is in the future')
        return False
    else:
        return True

# Given company, start year, end year, return relevant list of company 10-K's
def collect_fin_statements(ticker, cik, start_year, end_year): #scale add: get_10Ks=True
    # get_index_years(start_year, end_year)
    get_10Ks(ticker, cik, start_year, end_year)
    pass

def extract_fcf_data():
    pass

#prepare a professional Free Cash Flow Statement (as detailed as is possible or that you see fit, but at least including the following:
#EBIT, NI, FCFF, FCFE, CCF).  Report these figures and also validate them by performing computations for FCFF, FCFE, and CCF using the alternate method
#(shown in class).

def calculate_fcf(EBIT, NI, FCFF, FCFE, CCF):
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

# Control flow
while True:
    TICKER = ""
    while not verify_ticker(TICKER): # query for ticker until get valid ticker
        TICKER = query_ticker()

    print(get_company_name(TICKER))
    CIK = get_CIK_from_ticker(TICKER) # fetch CIK from ticker
    print('CIK: ', CIK)

    START_YEAR = None
    END_YEAR = None
    while not verify_date_range(START_YEAR, END_YEAR, TICKER): # query for date range until date range valid
        START_YEAR, END_YEAR = query_date_range(TICKER, CIK)

    all_statements_between_years = collect_fin_statements(TICKER, CIK, START_YEAR, END_YEAR) # if date range valid, collect relevant statements
    fcf = extract_fcf_data(all_statements_between_years) # extract needed data for FCF statement
    calculate_fct(EBIT, NI, FCFF, FCFE, CCF) # calculate FCF line items
    export(fcf) # export FCF line items to formatted csv

    if not another_query_needed(): # check if another query needed
        exit
