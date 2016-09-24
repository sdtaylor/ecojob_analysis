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

    #Go thru table of contents and identify actual positions in table rows
    #by having a link that starts with # (the link to the full position farther down).
    page_entries=[]
    page_short_links=[]
    for table_row in soup.find_all('tr'):
        if table_row.a and table_row.a.has_attr('href'):
            row_link=table_row.a['href']
            if row_link[0]=='#' and row_link not in page_short_links:
                columns=table_row.find_all('td')

                #Skip malformed columns
                if len(columns) != 4:
                    print('malformed column, skipping row on page: '+ page_info['url'])
                    break

                this_entry={}
                this_entry['location']=columns[location_position].text
                this_entry['title']=columns[title_position].text
                this_entry['close_date']=columns[2].string
                this_entry['post_date']=columns[3].string
                this_entry['toc_short_link']=row_link
                this_entry['position_type']=page_info['position_type']
                page_entries.append(this_entry)

                #Keep track of entries so featured ones don't get counted twice. 
                page_short_links.append(row_link)

    #TODO: Go thru them all again, finding the main text and collecting that.
    #Collect the main text of the ads. 
    #Get all a and p tags. When an a tag has an id value in the short link list,
    #the next entry should be the main text for that short link.
    #Because of the way it's formated the *next* short link in the list is inside
    #the main body text, so remove that (it's always the last link).
    #A little wonky, but it works. 
    a_p_tags=soup.find_all(['a','p'])
    for i,entry in enumerate(a_p_tags):
        if entry.has_attr('id') and '#'+entry['id'] in page_short_links:
            full_text=a_p_tags[i+1]

            #Don't fail if there is nothing to extract. Happens on the very last entry of pages
            try:
                full_text.find_all('a')[-1].extract()
            except IndexError:
                pass

            short_link='#'+entry['id']
            entry_index=page_short_links.index(short_link)

            page_entries[entry_index]['full_text']=full_text.text
            page_entries[entry_index]['text_short_link']=short_link


    return(page_entries)

####################################################################################
#Build list of pages to download

#The main page types and year prefixes for all the archives
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
#Main

if __name__ == __main__:
    all_entries=[]
    for this_page in all_pages:
        print(this_page)
        page_entries=compile_single_page(this_page)
        #None gets returned if there was a 404 error
        if page_entries:
            all_entries.extend(page_entries)

    all_entries=pd.DataFrame(all_entries)
    all_entries.to_csv('duke_esa_archive.csv',index=False)
