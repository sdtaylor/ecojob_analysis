import urllib.request as urllib
from bs4 import BeautifulSoup
import pandas as pd
import random
from time import sleep
import sqlalchemy


def compile_single_page(page_info):
    #Account for 404 errors
    try:
        soup=BeautifulSoup(urllib.urlopen(page_info['url']),'lxml')
    except:
        return None

    #Postdoc and faculty pages have title in the 1st column, location
    #in the 2nd. All other pages are flipped
    if page_info['position_type'] in ['faculty','postdoc']:
        title_position=0
        location_position=1
    else:
        title_position=1
        location_position=0

    #Go tru table of contents and identify actual positions in table rows
    #by having a link that starts with # (the link to the full position farther down).
    #Post date, and link to main text
    page_entries=[]
    page_short_links=[]
    for table_row in soup.find_all('tr'):
        if table_row.a:
            row_link=table_row.a['href']
            if row_link[0]=='#' and row_link not in page_short_links:
                this_entry={}
                this_entry['location']=table_row.find_all('td')[location_position].string
                this_entry['title']=table_row.find_all('td')[title_position].string
                this_entry['close_date']=table_row.find_all('td')[2].string
                this_entry['post_date']=table_row.find_all('td')[3].string
                this_entry['short_link']=row_link
                this_entry['position_type']=page_info['position_type']
                page_entries.append(this_entry)

                #Keep track of entries so features ones don't get counted twice. 
                page_short_links.append(row_link)

    #Go thru them all again, finding the main text and collecting that.
    for this_entry in page_entries:
        pass

    return(page_entries)

####################################################################################
#Build list of pages to download

#The main page types and year prefixes for all teh archives
position_types=['faculty','postdoc','grad','staff','temp','undergrad']
position_years=['2015','2014','2013','2012','11','10','09','08','07','06','05','04','03','02','01','00']

base_url='http://esa-ecophys.org/'

all_pages=[]
for this_type in position_types:
    for this_year in position_years:
        this_page={}
        this_page['url']=base_url+this_year+this_type+'.html'
        this_page['position_type']=this_type
        all_pages.append(this_page)


##########################################################3

all_entries=[]
for this_page in all_pages[3:20]:
    all_entries.extend(compile_single_page(this_page))

all_entries=pd.DataFrame(all_entries)
all_entries.to_csv('duke_esa_archive.csv',index=False)
