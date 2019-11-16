#!/usr/bin/env python
# coding: utf-8

# In[3]:


#def get_import():
import requests
from lxml import html
from bs4 import BeautifulSoup
import re
from datetime import date
import pandas as pd


# In[4]:


#get_import()


# ### GET TICKER FROM USER (VALIDATION INCLUDED)

# In[6]:


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
           
            print(baselink)#DEBUG
            
            #convert user input to lowercase for search
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
                comp_name = list(soup.find_all('span', class_ = 'companyName'))[0].                text.replace('(see all company filings)','')

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


# ### GET THE DATE SEARCH RANGE A SEPRATE DATE VALIDATION

# In[96]:


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
    if start> current_date or start < 19900101 or end <19900101 or end < start:
        print('Please check the year entry. The application do not support search prior to 1990.')
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
def get_year():
    
    right_year = False
    while right_year == False:
        print('Date format: YYYYMMDD')
        start_year = input('optional - Search Start year (Press enter to pass):')
        end_year = input('optional - Search end year (Press enter to pass):')
        right_year = date_validation(start_year , end_year)
    return right_year


# ### GET FILE TYPE (10-K ONLY SO FAR)

# In[53]:


#get the file type
#so far only returns '10-k'
def get_file_type():
    filetype = False
    while filetype == False:
        filetype = input ('what document are you looking for?')
        if filetype == '':
            filetype = False
        else:
            if filetype == '10k' or filetype =='10 k' or filetype =='10-k'            or filetype =='10K' or filetype =='10 K' or filetype =='10-K':
                return '10-K'
            else:
                print('Please check the file type!')
                filetype = False
    


# In[ ]:





# In[ ]:





# In[71]:


# def get_files(CIK, search_range,file_type):
CIK = int('0001652044')
search_range = [2017,2018]
file_type = '10-K'

baselink = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&            CIK={}&type={}&dateb={}&owner=exclude&count=100'

#break date_range into start and end, link only takes dates prior to XXXX
start_year = search_range[0]
end_year = search_range[1]
#fill link
link = baselink.format(CIK,file_type,end_year)

#get html content
page = requests.get(link)
soup = BeautifulSoup(page.content, 'html.parser')
print(soup)




# In[65]:


def main():
    comp_name = get_ticker()
    search_range = get_year()
    file_type = get_file_type()




