import urllib.request as urllib
from bs4 import BeautifulSoup
import pandas as pd
import random
from time import sleep
import sqlalchemy


#Get links for all the week links in main ecolog archive page
def get_week_links(url):
    soup=BeautifulSoup(urllib.urlopen(url), 'lxml')
    link_list=[]
    #First 4 entries of this type are admin links
    for line in soup.find_all('li')[4:]:
        link_list.append(line.a['href'])
    return(link_list)


#Get the links for individual messages givin a url for a single archive week
def get_message_links(url):
    soup=BeautifulSoup(urllib.urlopen(url), 'lxml')
    link_list=[]
    for line in soup.find_all('li'):
        #Skip the 1st list of messages that acts as a toc
        if line.a.has_attr('name'):
            #Within the each message description, the 2nd <a> tag
            #is the link to the actual message. If there are multiple
            #messages in a thread, this will also get the link to only the 
            #first message, ignoring any replies. Suitable for only
            #grabbing job ads
            link_list.append(line.find_all('a')[1]['href'])

    return(link_list)

#Get the contents of a single mesage
def get_message_content(url):
    print(url)
    print('')
    soup=BeautifulSoup(urllib.urlopen(url), 'lxml')
    message={}
    message['subject']=''
    message['date']=''
    message['body']=''

    #Pull out email subject and date
    for line in soup.find_all('span'):
        if line['id']=='MSGHDR-Subject-PRE':
            message['subject']=line.string
        elif line['id']=='MSGHDR-Date-PRE':
            message['date']=line.string 

    #Pull out email message body. Not identified the same way as
    #subject and date.
    message['body']=soup.find('pre').p.text

    return(message)

#Storing data and writing it to a DB every now
#and then to not fill up memory
class data_store:
    def __init__(self, sql_file, chunk_size=3):
        self.db_engine=sqlalchemy.create_engine(sql_file)
        self.message_store=[]
        self.chunk_size=chunk_size

    def write_db(self):
        df=pd.DataFrame(self.message_store)
        df.to_sql('ecolog', self.db_engine, if_exists='append', index=False)
        df=[]
        self.message_store=[]

    def add_entry(self, new_entry):
        self.message_store.append(new_entry)
        #print(len(self.message_store))
        #print(new_entry)
        if len(self.message_store) >= self.chunk_size:
            self.write_db()


###############################################
#TODO: fix memory filling up every few years of data. 

base_url='https://listserv.umd.edu/'
datafile='sqlite:///ecolog_archive.sqlite'
add_delay=True

all_messages=data_store(datafile)
error_log=0
for weekly_archive_link in get_week_links(base_url+'archives/ecolog-l.html'):
    for message_link in get_message_links(base_url+weekly_archive_link):
        try:
            all_messages.add_entry(get_message_content(base_url+message_link))
        except:
            error_log+=1

        #Try not to overload the webserver
        if add_delay:
            sleep(1+random.random())

all_messages.write_db()
print('Errors: '+str(error_log))
