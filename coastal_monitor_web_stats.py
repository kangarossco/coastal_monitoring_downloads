# Name:     coastal_monitor_web_stats.py
# Date:     May 13, 2021
# Author:   Ross McKinnon
# email:    srossmckinnon@gmail.com
# github    @kangarossco
#
# Program scrapes viewcount and download count from 11 coastal monitoring websites on the opendata portal
# https://data.novascotia.ca/ and saves to two .csvs locally
#
# the website is dynamic so selenium must be used to enable javascript

#selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import time
from datetime import datetime
from os import path

#function writes a list to a csv that already has a header
def write_to_file(filepath,data):
    f = open(filepath, "a+")
    for x in data:
        f.write("{}," .format(x))
    f.write("\n")
    f.close()

#function creates a csv if it doesn't already exist and writes a header to it. Calls write_to_file to write data 
def make_or_use(filepath, headers, data):
    tempfilepath = path.join(working_dir,filepath)
    if not path.exists(tempfilepath):
        write_to_file(tempfilepath,headers)
    write_to_file(tempfilepath,data)
    
#set up chrome driver only once
driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"

options = Options()
options.headless = True
driver = webdriver.Chrome(driver_path, options=options)

#these datasets are easliy iteratable
codes = {
    "Annapolis" : "knwz-4bap",
    "Digby" : "wpsu-7fer",
    "Guysborough" : "eb3n-uxcb",
    "Halifax" : "x9dy-aai9",
    "Inverness" : "a9za-3t63",
    "Lunenburg" : "eda5-aubu",
    "Pictou" : "adpu-nyt8",
    "Richmond" : "v6sa-tiit",
    "Shelburne" : "mq2k-54s4",
    "Yarmouth" : "9qw2-yb2f",
    "Station-Locations" : "cjfb-f4d4"
    }

#since it's a .csv that is constantly being added to we will just use lists and add as neccesary. no dataframes
#this section is the datasets (11 pages)
titles = []
views = []
downloads = []
webone = "https://data.novascotia.ca/Nature-and-Environment/Coastal-Monitoring-Program-"

for key in codes:
    if key != "Station-Locations":
        ident = "Data-"
    else:
        ident = ""

    url = webone + ident + key + "/" + codes[key]
    driver.get(url)

    #uncomment if there are issues
    #time.sleep(2)

    html_page = driver.page_source
    soup = BeautifulSoup(html_page, 'html.parser')
    data = soup.find_all("dd", class_="metadata-pair-value")

    titles.append(soup.title.text)
    views.append(int(data[1].text))
    downloads.append(int(data[2].text))

#this group is the graphs (10 pages)
#the format changes up a bit so to save time, I just used a list with most of the url isntead of iterating through a dictionary
websites2 = ["Annapolis-County-Daily-/a3qb-nf5k",
             "Data-Digby-County-Daily/yeii-vbir",
             "Data-Inverness-County-D/njv9-c7a6",
             "Data-Pictou-County-Dail/pmim-yujz",
             "Guysborough-County-Dail/gvmv-b2s3",
             "Halifax-County-Daily-Av/vpt7-apvp",
             "Lunenburg-County-Daily-/xg2s-uhbg",
             "Richmond-County-Daily-A/5p9y-iyag",
             "Shelburne-County-Daily-/5ech-4c5t",
             "Yarmouth-County-Daily-A/bbrp-vuad"]

graphs_views = []
webtwo = "https://data.novascotia.ca/Nature-and-Environment/Coastal-Monitoring-Program-"

#the viewcount for this set of pages needs to be activated by clicking a 'more info' button
more_info = '//*[@id="app"]/div/div[2]/div[1]/div/div[1]/div[2]/button'

for county in websites2:
    url = webtwo + county
    driver.get(url)

    #page needs to load before clicking on it
    time.sleep(2)
    
    driver.find_element_by_xpath(more_info).click()

    html_page = driver.page_source
    soup = BeautifulSoup(html_page, 'html.parser')
    data2 = soup.find_all("span", class_="date")
    
    graphs_views.append(int(data2[1].text))

#all scraping is done
driver.quit()

#trims the page names so it's just the location
#use this for the graphs aswell just stop before the last element because there is no 'station locations' graph page
for title in range(len(titles)):
    titles[title] = titles[title][titles[title].find(":") + 2 : titles[title].find("|") - 1]

#add timestamp at index 0
titles.insert(0, "Time")
views.insert(0, str(datetime.now()))
downloads.insert(0, str(datetime.now()))
graphs_views.insert(0, str(datetime.now()))

#all csv will be saved to same directory, 
working_dir = ""

#dataset downloads
down = "dataset_downloads.csv"
make_or_use(down,titles,downloads)

#dataset views
view = "dataset_views.csv"
make_or_use(view,titles,views)

#graph views
graph_views_file = "graph_views.csv"
titles.pop(-1)
make_or_use(graph_views_file,titles,graphs_views)
