import pandas as pd

###################################
#Turn MM/DD/YY into YYYY-MM-DD
import datetime
def clean_date(d):
    try:
        new_d = datetime.datetime.strptime(d,'%m/%d/%y').strftime('%Y-%m-%d')
    except:
        new_d = None
    return new_d
##################################
#Get coordinates of places using openstreetmap api
from geopy.geocoders import Nominatim
geolocator = Nominatim()
def get_coordinates(location_string):
    try:
        location_info = geolocator.geocode(location_string)
    except:
        location_info = None

    if location_info:
        return location_info.latitude, location_info.longitude
    else:
        return None, None
#################################
def isNan(x):
    return x==x

################################
#Main
################################
data_raw = pd.read_csv('duke_esa_archive.csv').to_dict('records')

data_cleaned=[]
for entry in data_raw:
    #Drop any entries that were not matched correctly between table of contents and
    #main text
    if not entry['toc_short_link'] == entry['text_short_link']: 
        print('Skipping entry: short links dont match')
        continue

    entry['post_date'] = clean_date(entry['post_date'])
    entry['close_date'] = clean_date(entry['close_date'])
    entry['latitude'], entry['longitude'] = get_coordinates(entry['location'])

    del entry['toc_short_link']
    del entry['text_short_link']

    data_cleaned.append(entry)

data_cleaned = pd.DataFrame(data_cleaned)
data_cleaned.to_csv('duke_esa_archive_cleaned.csv', index=False)
