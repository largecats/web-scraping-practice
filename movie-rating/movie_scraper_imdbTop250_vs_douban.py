##################################################
#                 import modules                 #
##################################################
import requests
from lxml import html
import re
import pandas as pd
import numpy as np
import time
import random
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

##################################################
#                 set up browser                 #
##################################################
chromedriver = "path-to\chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver

options = webdriver.ChromeOptions()
# do not load images  
prefs = {  
     'profile.default_content_setting_values': {  
        'images': 2 
    }  
}  
options.add_experimental_option('prefs',prefs)  
  
browser = webdriver.Chrome(chromedriver, chrome_options = options)
browser.set_page_load_timeout(30)

browser.get('https://movie.douban.com')
assert "豆瓣电影" in browser.title

##################################################
#                   main loop                    #
##################################################
# set working directory
path = ""
os.chdir(path)

# declare lists to store data
names = []
years = []
genres = []
imdbRatings = []
doubanRatings = []
regions = []

# make request
response = requests.get("http://www.imdb.com/chart/top")

# parse page
pageHtml = BeautifulSoup(response.text, 'html.parser')

for i in range(0,250):

    # pause loop to avoid bombarding the site with requests
    sleep(randint(3, 5))

    # scrape name
    titleInfo = pageHtml.find_all('td', class_ = 'titleColumn')[i]
    name = titleInfo.a.text
    names.append(name)

    # scrape year
    year = titleInfo.span.text
    pattern = re.compile(r'(\d{4})', flags=re.DOTALL)
    year = (pattern.findall(year))[0]
    years.append(year)

    # enter imdb movie page
    imdbMovieUrl = 'http://www.imdb.com' + titleInfo.a.get('href')
    imdbMoviePage = requests.get(imdbMovieUrl)
    imdbMoviePageHtml = BeautifulSoup(imdbMoviePage.text, 'html.parser')
    print(imdbMovieUrl)

    # scrape imdb rating
    pattern = re.compile(r'<span itemprop="ratingValue">(.+?)</span>', flags=re.DOTALL)
    imdbRating = float(pattern.findall(imdbMoviePage.text)[0])
    imdbRatings.append(imdbRating)

    # scrape genre
    pattern = re.compile(r'<span class="itemprop" itemprop="genre">(.+?)</span>', flags=re.DOTALL)
    genre = pattern.findall(imdbMoviePage.text)
    genre = ", ".join(genre)
    genres.append(genre)

    # scrape region
    detailsInfo = imdbMoviePageHtml.select('div#titleDetails')[0]
    textBlocks = detailsInfo.find_all('div', class_="txt-block")
    for t in textBlocks:
        if 'Country' in t.text:
            regionInfo = t
            break
    region = regionInfo.a.text
    regions.append(region)

    # scrape douban rating
    keywords = name + " " + year
    # find the searchbox element
    elem = browser.find_element_by_name("search_text")
    # clear search box
    elem.clear()
    # enter in search box
    elem.send_keys(keywords)
    elem.send_keys(Keys.RETURN)
    searchPageHtml = BeautifulSoup(browser.page_source, "lxml")
    containers = searchPageHtml.find_all('div', class_ = 'item-root')
    j = 0
    while j < len(containers):
        firstContainer = containers[j]
        titleInfo = firstContainer.find('div', class_="title").text
        # only scrape rating if result has matching title and year
        if name in titleInfo and year in titleInfo:
            doubanRating = float(firstContainer.find("span", class_ = "rating_nums").text)
            break
        else:
            j += 1
    if j == len(containers):
        doubanRating = "NA"
    doubanRatings.append(doubanRating)

    print(keywords, genre, region, imdbRating, doubanRating)

movieInfo = pd.DataFrame({'movie': names,
                              'year': list(map(int,years)),
                              'genre': genres,
                              'imdb': imdbRatings,
                              'douban': doubanRatings,
                              'region': regions},
                              columns = ['movie','year','genre','imdb','douban','region'])
movieInfo.index = movieInfo.index + 1

print(movieInfo.info())
print(movieInfo.head(10))
fileName = "IMDBTop250vsDouban.csv"
movieInfo.to_csv(fileName, sep = ",", encoding = "utf-8", index = False)

