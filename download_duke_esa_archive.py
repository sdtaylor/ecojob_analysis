import urllib.request as urllib
from bs4 import BeautifulSoup
import pandas as pd
import random
from time import sleep
import sqlalchemy


def compile_single_page(url):
    soup=BeautifulSoup(urllib.urlopen(url),'lxml')
    #1st go thru the index at the top colelcting Title, Location, Review Date, 
    #Post date, and link to main text
    all_entries=[]
    for table_row in soup.find_all('table')[1].find_all('tr'):
        this_entry={}
        this_entry['location']=table_row.a.string
        this_entry['title']=table_row.find_all('td')[1]
        this_entry['close_date']=table_row.find_all('td')[2]
        this_entry['post_date']=table_row.find_all('td')[3]

    #Go thru them all again, finding the main text and collecting that.

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



