import urllib.request as urllib
from bs4 import BeautifulSoup
import pandas as pd
import random
from time import sleep


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
    message['body']=soup.find('pre').p.string

    return(message)

###############################################

base_url='https://listserv.umd.edu/'
datafile='ecolog_archive.csv'
add_delay=False

all_messages=[]
for weekly_archive_link in get_week_links(base_url+'archives/ecolog-l.html')[1:4]:
    for message_link in get_message_links(base_url+weekly_archive_link):
        all_messages.append(get_message_content(base_url+message_link))
        #Try not to overload the webserver
        if add_delay:
            sleep(random.randint(1,3)+random.random())

all_messages=pd.DataFrame(all_messages)
all_messages.to_csv(datafile, index=False)
