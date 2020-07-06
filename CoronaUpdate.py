from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import datetime
import pickle

def rows_to_list(rows_objects):
    return [row_object.text.split("\n") for row_object in rows_objects]

def print_rows(page_rows):
    for row in page_rows:
        print(row)

def unite_pages(pages):
    all_rows = []
    for page in pages:
        for row in page:
            all_rows.append(row)
    return all_rows

# 2-D arrays - [page in website][row number]
def get_new_rides(yesterday_rides, today_rides):
    yesterday_rides = unite_pages(yesterday_rides)
    today_rides = unite_pages(today_rides)

    new_rides = [ride for ride in today_rides if ride not in yesterday_rides]
    if new_rides == []:
        print("no new rides")
    return new_rides

binary = r'Mozilla Firefox\firefox.exe'

options = Options()
options.add_argument("-headless")
options.add_argument("headless")
options.add_argument("--headless")

options.headless = True
options.binary = binary
cap = DesiredCapabilities().FIREFOX
# cap["marionette"] = True #optional
driver = webdriver.Firefox(options=options, executable_path="geckodriver-v0.26.0-win64\\geckodriver.exe")#, capabilities=cap)

driver.get("https://coronaupdates.health.gov.il/corona-updates/grid/public-transport")
yesterday = datetime.date.today() - datetime.timedelta(days=1)

page_counter = 0

all_rows = []
prev_rows = []

page_rows =  rows_to_list(driver.find_elements_by_class_name("mat-row"))

while(len(page_rows) == 0):
    print("loading website.. sleeping 10 seconds..")
    time.sleep(10)
    page_rows = rows_to_list(driver.find_elements_by_class_name("mat-row"))

print("extracting rides")
page_counter = page_counter + 1
rides_counter = len(page_rows)
#
while(prev_rows != page_rows): # until we reach last page
    all_rows.append(page_rows)
    prev_rows = page_rows
    driver.find_element_by_xpath("//button[@class='moh-icon grid_ar_prev page-button']").click() #next page
    page_rows = rows_to_list(driver.find_elements_by_class_name("mat-row"))

    if (prev_rows != page_rows):
        rides_counter = rides_counter +  len(page_rows)
        page_counter = page_counter + 1

print ("done loading")
#
full_time = time.localtime()

full_date = "{}_{}_{}".format(full_time.tm_mday,full_time.tm_mon,full_time.tm_year)

pickle.dump(all_rows, open("all_rows_{}".format(full_date), "wb"))
print("pages: {}".format(page_counter))
print("rides count: {}".format(rides_counter))

days_index = pickle.load(open("days_index", "rb"))

if (days_index[-1] == full_date): # rerun!
    print("rerun!")
    last_day = days_index[-2].split("_")  # DD*_MM*_YYYY

else: # normal
    last_day = days_index[-1].split("_")

if full_date not in days_index:
    days_index.append(full_date)
    pickle.dump(days_index, open("days_index", "wb"))

yesterday_all_rows = "all_rows_{}_{}_{}".format(last_day[0],last_day[1],last_day[2])
yesterday_rides = pickle.load(open(yesterday_all_rows, "rb"))

print_rows(get_new_rides(yesterday_rides, all_rows))
driver.quit()