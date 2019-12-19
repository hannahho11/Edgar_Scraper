
import requests
from lxml import html
from bs4 import BeautifulSoup
import re
from datetime import date
import pandas as pd
import requests
import urllib.request
from IPython.display import display_html

#returns the company's CIK
def get_ticker():
    comp = False
    while comp == False:
        comp = input('Please enter the ticker for the company you want to search(required):')
        if comp == '':
            comp = False
        else:
            #get the search page 
            #count = 5 so parse fast since we are just getting the name of company
            baselink = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=&dateb=&owner=exclude&count=5'
            #search lowercase 
            comp = comp.lower()
            url = baselink.format(comp)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            #see if no match is found 
            no_match = soup.find_all('h1')

            #if not found 
            if len(list(no_match))!=0:
                print(no_match[0].text)
                print('Please try again')
                comp = False
            #when there is a match, check if right match
            else:
                comp_name = list(soup.find_all('span', class_ = 'companyName'))[0].\
                text.replace('(see all company filings)','')

                right_company = False
                #ask the user if they is what they are looking for
                right_company = False
                while right_company == False:
                    print('')
                    print('')
                    print('Is this the company you are looking for? (Press Y for yes N for no)')
                    right_company = input(comp_name)
                    if right_company.upper() != 'Y' and right_company.upper() !='N':
                        right_company = False
                    elif right_company.upper() == 'N':
                        comp = False
                    else: 
                        return comp_name.split(' ')[-2]



#check if the date entered is valid 
#returns either False or valid date as pair [start,end]
def date_validation(start, end):
    current_date = int(date.today().strftime('%Y%m%d'))
    
    #ignore if empty start and end
    if start == '' and end == '':
        return ['','']
    #check format length
    if len(start) != 8 or len(end)!=8:
        print('Please check date entered!')
        return False
    
    #see if user entered the right date
    try:
        start_test = pd.to_datetime(start,format='%Y%m%d')
        end_test = pd.to_datetime(end,format='%Y%m%d')
    #when the user enter the wrong content - entering anyting other than numbers 
    except:
        print('Please enter the right date (numbers only)')
        return False
    start = int(start)
    end = int(end)
    #check if reasonable begin &end date
    if start> current_date or start < 20090501 or end <20090501 or end < start:
        print('Please check the year entry. The application do not support search prior to May 2009.')
        return False
    else:
        #if user's end year > this year, then end year would be this year
        if end > current_date:
            end = current_date
            return[start,end]
        else:
            right_year = True
            return[start,end]   
        
        
#asking for the end year start year
#return the final search range. format: list[startdate, enddate]
def get_year():
    
    right_year = False
    while right_year == False:
        print('Date format: YYYYMMDD')
        start_year = input('optional - Search Start year (Press enter to pass):')
        end_year = input('optional - Search end year (Press enter to pass):')
        right_year = date_validation(start_year , end_year)
    return right_year



#get the file type
#so far only returns '10-k'
#returns true or false
def get_file_type():
    filetype = False
    while filetype == False:
        filetype = input ('what document are you looking for?')
        if filetype == '':
            filetype = False
        else:
            if filetype == '10k' or filetype =='10 k' or filetype =='10-k'\
            or filetype =='10K' or filetype =='10 K' or filetype =='10-K':
                return '10-K'
            else:
                print('Please check the file type!')
                filetype = False


#returns a page worth of html
def get_files(CIK, search_range,file_type):

    baselink = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}&dateb={}&owner=exclude&count=100'

    #break date_range into start and end, link only takes dates prior to XXXX
    start_year = search_range[0]
    end_year = search_range[1]
    #fill link
    link = baselink.format(CIK,file_type,end_year)

    #get html content
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


#get the table that contain the information
#returns a dataframe
def get_files_df(soup,search_range):
    file_rows = list(soup.find_all('tr'))[3:]

    #create list that contain each file's information
    f_types =[]
    f_links =[]
    f_dates = []
    sec_link = 'http://sec.gov'

    #create list that contain each file's information
    for row in file_rows:
        
        #gets file date
        file_type = row.find_all('td',{'nowrap':'nowrap'})[0].text
        file_date = row.find_all('td')[3].text.replace('-','')
        file_link = sec_link+row.find_all('td',{'nowrap':'nowrap'})[1].find_all('a', href = True)[0]['href']

        #this gets every item's file link
        if int(file_date) >int(search_range[0]) and int(file_date)<int(search_range[1]) and file_type == '10-K':
            f_types.append(file_type)
            f_dates.append(file_date)
            f_links.append(file_link)


    #construct a table:
    #['file type']: 10-k | ['file link']: sec.gov/Archive/....| ['file date': 19960303]
    files_table = pd.DataFrame({'file type':f_types,'file link':f_links,'file date':f_dates})
    return files_table


#filter dates since SEC only allows search with 'prior to'
#filter out non-10k item (e.g. 10-k/a...)
#returns a dataframe
def filtered_df(search_range,file_type,files_table):
#     #filter date
#     date_filtered = files_table[files_table['file date']>search_range[0]]
#     date_filtered
#     date_filtered = date_filtered[date_filtered['file date']<search_range[1]]
#     #filter file type
#     type_filtered = date_filtered[date_filtered['file type']=='10-K']
    return files_table

#get links for file 
#returns a list of links
def get_list_doc_link_text(filtered_df):
    sec_link = 'http://sec.gov'
    file_links = filtered_df['file link'].tolist()
    doc_links = []
    for URL in file_links:
        page_specific_10k = requests.get(URL)
        soup = BeautifulSoup(page_specific_10k.content, 'html.parser')
        complete_file_link = soup.find_all('table')[0].find_all('tr')[-1].\
                                        find_all('a',href = True)[0]['href']
        doc_full_link = sec_link + complete_file_link
        doc_links.append(doc_full_link)
    return doc_links
def get_link(filtered_df):
    return filtered_df['file link']

#No actual return just print caluclation
def calculation(links):
    print('\n')
    print('\n')
    for link in links:
        #read the txt from link
        broken_xml = urllib.request.urlopen(link).read().decode('utf-8')
        #break the thing into pages
        pages = broken_xml.split('page-break')
        #list the documents that we are looking for 
        documents = ['Consolidated Statements of Cash Flows','Consolidated Statements of Operations', 'Consolidated Statements of Comprehensive Income', 'Consolidated Balance Sheets', 'CONSOLIDATED STATEMENTS OF STOCKHOLDERS']
        
        #if the name of statements are found in any of the page
        #put the found statement's name and the text content into a list 
        doc_list = []
        for page in pages:
            idx = pages.index(page)
            found = 0
            for i in documents:
                if i.upper() in page:
                    key = i
                    found = +1
                    

            if found>=1:
                pair = [key,page]
                doc_list.append(pair)
        
        #write a html that contains the statements for testing purpose
        file = open('test.html','w')
        for i in doc_list:
            file.write(i[1])
        file.close()
        
        #create a list called statements to include the followin
        #include the name of the statemets and the actual statemet with numbers in dataframe
        #dataframe is raw data 
        statements = []
        for pair in doc_list:
            name = pair[0]
            page = pair[1]

            #parse page
            file_soup = BeautifulSoup(page, 'html.parser')
            #find the table element
            table = str(file_soup.find_all('table'))
            #get the table to a dataframe and use the line title as index
            df = pd.read_html(table)[0].iloc[3:,:].dropna(axis = 1, how = 'all').fillna(0)
            head = df.iloc[0]
            df = df[1:]
            df.columns = head
            df[0] = df[0].apply(lambda x:x.replace('(','').replace(')','').replace('','').replace(',','').replace(';','').replace('0',''))
            df = df.set_index(0)
            #append the pair([name, df])
            pair = [name,df]
            statements.append(pair)
            
        
        #create a clean statement list
        clean_statements = []
        for pair in statements:
            name = pair[0]
            table = pair[1]
            #separate way to clean other statements
            if name != 'CONSOLIDATED STATEMENTS OF STOCKHOLDERS':
                #get the final number of columns
                column_number = int(len(table.columns)/3)
                #get the final column names
                column_name = table.columns.drop_duplicates().tolist()
                #get the line names
                column_index = table.index.tolist()
                clean = pd.DataFrame()
                clean['index'] = column_index
                clean = clean.set_index('index')
                #get the correct column data to append to the clean dataframe
                for i in range(0,column_number):
                    which_column = (i+1)*3-2
                    content = table.iloc[:,which_column].values
                    column_name_clean = column_name[i]
                    clean[column_name_clean] = content

                pair = [name,clean]
                clean_statements.append(pair)
            
            #clean stocker holder's equity table
            #same code with column selection different
            if name == 'CONSOLIDATED STATEMENTS OF STOCKHOLDERS':
                column_number = int(len(table.columns)/3)
                column_name = table.columns.drop_duplicates().tolist()
                column_index = table.index.tolist()
                clean = pd.DataFrame()
                clean['index'] = column_index
                clean = clean.set_index('index')
                for i in range(0,column_number):
                    if i ==0:
                        which_column = 0
                    else:
                        which_column = i*3
                    content = table.iloc[:,which_column].values
                    column_name_clean = column_name[i]
                    clean[column_name_clean] = content

                pair = [name,clean]
                clean_statements.append(pair)
        
        #set variables used for calculation
        revenue = 0
        COGS = 0
        GrossProfit= 0 
        OPEX = 0
        DEPEX = 0
        tax = 0
        NOPAT= 0
        OCF =0
        CAPEX =0
        NWC = 0
        
        #grab numbers from the dataframes
        for statement in clean_statements:
            name = statement[0]
            chart = statement[1]
            if name == 'Consolidated Statements of Cash Flows':
                DEPEX = int(chart.loc['Depreciation of property and equipment including internal-use software and website development and other amortization including capitalized content costs'][0].replace('(','').replace(',',''))
                tax = int(chart.loc['Cash paid for income taxes net of refunds'][0].replace('(','').replace(')','').replace(',',''))
                CAPEX = int(chart.loc['Purchases of property and equipment including internal-use software and website development net'][0].replace('(','').replace(')','').replace(',',''))
            if name == 'Consolidated Statements of Operations':
                revenue = int(chart.loc['Total net sales'][0].replace('(','').replace(',',''))
                OPEX = int(chart.loc['Total operating expenses'][0].replace('(','').replace(',',''))
            if name == 'Consolidated Balance Sheets':
                #capex calcualtion
                cap_current = int(chart.loc['Property and equipment net'][0].replace('(','').replace(',',''))
                cap_previous = int(chart.loc['Property and equipment net'][1].replace('(','').replace(',',''))
                #CAPEX = cap_current - cap_previous + DEPEX

                #change in nwc
                previous_nwc_asset = int(chart.loc['Total current assets'][1].replace('(','').replace(',',''))
                previous_nwc_liability = int(chart.loc['Total current liabilities'][1].replace('(','').replace(',',''))
                current_nwc_asset = int(chart.loc['Total current assets'][0].replace('(','').replace(',',''))
                current_nwc_liability = int(chart.loc['Total current liabilities'][0].replace('(','').replace(',',''))
                previous_nwc =  previous_nwc_asset- previous_nwc_liability
                current_nwc =  current_nwc_asset- current_nwc_liability
                NWC = current_nwc - previous_nwc
                
        #calculating numbers
        GrossProfit = revenue - COGS
        EBIT  = GrossProfit - OPEX - DEPEX
        NOPAT = EBIT -tax
        OCF = NOPAT +DEPEX
        FCFF = OCF - CAPEX-NWC
        
        
        ##print result
        print('============================================')
        print('Calculation')
        print('--------------------------------------------')
        print('--------------------------------------------')
        print ('revenue','\t',revenue)
        print('COGS','\t\t','-',COGS)
        print('----------------------')
        print('Gross Profit','\t',GrossProfit)
        print('OPEX','\t\t','-',OPEX)
        print('DEPEX','\t\t','-',DEPEX)
        print('----------------------')
        print('EBIT','\t\t',EBIT)
        print('tax','\t\t','-',tax)
        print('----------------------')
        print('NOPAT','\t\t',NOPAT)
        print('DEPEX','\t\t','+',DEPEX)
        print('---------------------')
        print('OCF','\t\t',OCF)
        print('CAPEX','\t\t','-',CAPEX)
        print('NWC','\t\t','-',NWC)
        print('---------------------')
        print('FCFF','\t\t',FCFF)
        print('============================================')



#print calculation for fcff
def main():
    comp_name = get_ticker()
    search_range = get_year()
    file_type = get_file_type()
    initial_search_html = get_files(comp_name,search_range,file_type)
    file_link_df = get_files_df(initial_search_html,search_range)
    filtered = filtered_df(search_range,file_type,file_link_df)
    files_list_links = get_list_doc_link_text(filtered)
    print('\n')
    print('\n')
    calculation(files_list_links)
    user = input('would you like to do another search? (please press n for no)')
    if user =='I really need another search please allow it the password is: Hook\' em!':
        main()
    else:
        print('Thank you!')


main() 
    
    



