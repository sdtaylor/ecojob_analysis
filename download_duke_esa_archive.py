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


    #Go thru them all again, finding the main text and collecting that.
