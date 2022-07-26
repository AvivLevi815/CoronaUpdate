from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from googlemaps import Client as GoogleMaps
import json
import datetime
import time
import pickle
import requests

from bs4 import BeautifulSoup, element

def rows_to_list(rows_objects):
    return [row_object.text.split("\n") for row_object in rows_objects]

def init_google():
    gmaps = GoogleMaps('AIzaSyAH-SEZ1C_8Kb1ACyPCZZpZAJKKDuWD3Ro')
    return gmaps

# call Google API- 
# get lat, lng by address + name.
def address_to_latlng(address, city, name, gmaps):
    if city.strip() == "":
        return {"lat": "null", "lng": "null"}
    try:
        print("requesting {}".format(name + " " + address + " " + city))
        geocode_result = gmaps.geocode(name + " " + address + " " + city)
        print("got it")
        return {"lat": geocode_result[0]['geometry']['location']['lat'], "lng": geocode_result[0]['geometry']['location']['lng']}
    except IndexError:
        print("Address was wrong... {} inserting null's".format(address))
        return {"lat": "null", "lng": "null"}
    except Exception as e:
        print("Unexpected error occurred.", e)


# unite all rows with same location to a dict
# Final format:
# {(lat, kng) : ["key": <unique key>,
#                "name":<location name>,
#                "city":<location city>,
#                "address":<location address>,
#                "location":<location lat, lng>, # original lat,lng 
#                "datetime": <datetime of corona case>}


def compress(jsons):
    by_coord = {}
    cur_key = 0
    for json in jsons:
        (lat, lng) = json["location"].values()
        location_tuple = (lat, lng)
        if location_tuple not in by_coord:
            by_coord[location_tuple] = {"key": cur_key, 'name': json['name'], 'city': json['city'], 'address': json['address'],
                                          'location': json['location'], 'datetime': []}

        by_coord[location_tuple]['datetime'].append({"key": cur_key, "date": json["date"],
                                                                                "time_start": json["time_start"],
                                                                                "time_end": json["time_end"]})
        cur_key = cur_key + 1
    return  by_coord


#convert every row of data to python dict
#use google API to retrieve coordinates
def rows_to_dicts(rows, gmaps = None):
    translations = {"ישוב" : "city", "מקום" : "name" , "כתובת": "address",
                    "החל מתאריך" : "date", "עד תאריך": "to_date","פירוט נוסף":"added information",
                    "החל משעה" : "time_start", "עד שעה": "time_end"}
    final_list_of_dicts = []
    for row in rows:
        row_dict = {}
        for child in list(row.children):
            if len(child) > 1: # not comment
                if   "שעה" not in  child.text:
                    key, value = child.text.split(":")
                else:
                    key = child.text[:child.text.index(":")]
                    value = child.text[child.text.index(":", ) + 1:].strip()
                row_dict[translations[key]] = value

        if row_dict["city"].strip() != "":
            row_dict["location"] = address_to_latlng(row_dict["address"], row_dict["city"], row_dict["name"], gmaps)
            final_list_of_dicts.append(row_dict)
    return final_list_of_dicts



def print_rows(page_rows):
    for row in page_rows:
        print(row)

# all rides to one list
def unite_pages(pages):
    all_rows = []
    for page in pages:
        for row in page:
            all_rows.append(row)
    return all_rows

# 2-D arrays - [page in website][row number]

# get only rides that did not exist in yesterday_rides
def get_new_rides(yesterday_rides, today_rides):
    yesterday_rides = unite_pages(yesterday_rides)
    today_rides = unite_pages(today_rides)

    new_rides = [ride for ride in today_rides if ride not in yesterday_rides]
    if new_rides == []:
        print("no new rides")
    return new_rides


print(time.localtime())

# Init Google API
gmaps = init_google()
binary = r'Mozilla Firefox\firefox.exe'

# Use headless browser
options = Options()
options.add_argument("--headless")

options.headless = True

#Browser location
options.binary = binary
cap = DesiredCapabilities().FIREFOX
# cap["marionette"] = True #optional

# set driver
driver = webdriver.Firefox(options=options, executable_path="geckodriver-v0.26.0-win64\\geckodriver.exe")#, capabilities=cap)
driver.get("https://coronaupdates.health.gov.il/corona-updates/grid/place")

all_rows = []
prev_rows = []

# init parser
soup = BeautifulSoup(driver.page_source, 'html.parser')
page_rows =  len(soup.findAll("mat-row"))
page_counter = 0

#scrape first page
while(page_rows == 0):
    print("loading website.. sleeping 10 seconds..")
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_rows = len(soup.findAll("mat-row"))

print("extracting places")
page_counter = page_counter + 1
place_counter = page_rows
page_rows = rows_to_dicts(soup.findAll("mat-row"), gmaps)

#scrape other pages
while(prev_rows != page_rows): # until we reach last page
    all_rows.append(page_rows)
    prev_rows = page_rows
    driver.find_element_by_xpath("//button[@class='moh-icon grid_ar_prev page-button']").click() #next page
    print("page {}".format(page_counter))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_rows = rows_to_dicts(soup.findAll("mat-row"), gmaps)
    if(page_counter == 1):
        break
    if (prev_rows != page_rows):
        place_counter = place_counter + len(page_rows)
        page_counter = page_counter + 1

print ("done loading")
full_time = time.localtime()

full_date = "{}_{}_{}".format(full_time.tm_mday,full_time.tm_mon,full_time.tm_year)

print("pages: {}".format(page_counter))
print("rides count: {}".format(place_counter))
for row in all_rows:
    print(row)
print("*********************************************************************")

compressed = compress(unite_pages(all_rows))

for_json = []
for coord in compressed:
    for_json.append(compressed[coord])

pickle.dump(for_json, open("db_pickle.json", "wb"))

print(time.localtime())

with open('db.json', 'w', encoding='utf-8') as outfile:
    json.dump(for_json,outfile, ensure_ascii=False)
driver.quit()


