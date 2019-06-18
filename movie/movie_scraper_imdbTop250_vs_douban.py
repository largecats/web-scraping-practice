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
from IPython.core.display import clear_output
from time import sleep
from random import randint
from warnings import warn
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

##################################################
#                 set up browser                 #
##################################################
chromedriver = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver

options=webdriver.ChromeOptions()  
prefs={  
     'profile.default_content_setting_values': {  
        'images': 2 
    }  
}  
options.add_experimental_option('prefs',prefs)  
  
browser = webdriver.Chrome(chromedriver, chrome_options=options)
browser.set_page_load_timeout(30)

browser.get('https://movie.douban.com')
assert "豆瓣电影" in browser.title

##################################################
#                   main loop                    #
##################################################
# declare lists to store data
names = []
years = []
genres = []
imdb_ratings = []
douban_ratings = []
regions = []

# make request
response = requests.get("http://www.imdb.com/chart/top")

# parse page
page_html = BeautifulSoup(response.text, 'html.parser')

for i in range(0,250):

    # pause loop to avoid bombarding the site with requests
    sleep(randint(3, 5))

    # scrape name
    title_info = page_html.find_all('td', class_ = 'titleColumn')[i]
    name = title_info.a.text
    names.append(name)

    # scrape year
    year = title_info.span.text
    pattern = re.compile(r'(\d{4})', flags=re.DOTALL)
    year = (pattern.findall(year))[0]
    years.append(year)

    # enter imdb movie page
    imdbMovieUrl = 'http://www.imdb.com' + title_info.a.get('href')
    imdbMoviePage = requests.get(imdbMovieUrl)
    imdbMoviePage_html = BeautifulSoup(imdbMoviePage.text, 'html.parser')
    print(imdbMovieUrl)

    # scrape rating
    pattern = re.compile(r'<span itemprop="ratingValue">(.+?)</span>', flags=re.DOTALL)
    imdb_rating = float(pattern.findall(imdbMoviePage.text)[0])
    imdb_ratings.append(imdb_rating)

    # scrape genre
    pattern = re.compile(r'<span class="itemprop" itemprop="genre">(.+?)</span>', flags=re.DOTALL)
    genre = pattern.findall(imdbMoviePage.text)
    genre = ", ".join(genre)
    genres.append(genre)

    # scrape region
    details_info = imdbMoviePage_html.select('div#titleDetails')[0]
    textBlocks = details_info.find_all('div', class_="txt-block")
    for t in textBlocks:
        if 'Country' in t.text:
            region_info = t
            break
    region = region_info.a.text
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
    searchPage_html = BeautifulSoup(browser.page_source, "lxml")
    containers = searchPage_html.find_all('div', class_ = 'item-root')
    j = 0
    while j < len(containers):
        first_container = containers[j]
        title_info = first_container.find('div', class_="title").text
        if name in title_info and year in title_info:
            douban_rating = float(first_container.find("span", class_ = "rating_nums").text)
            break
        else:
            j += 1
    if j == len(containers):
        douban_rating = "NA"
    douban_ratings.append(douban_rating)

    print(keywords, genre, region, imdb_rating, douban_rating)

movie_info = pd.DataFrame({'movie': names,
                              'year': list(map(int,years)),
                              'genre': genres,
                              'imdb': imdb_ratings,
                              'douban': douban_ratings,
                              'region': regions},
                              columns = ['movie','year','genre','imdb','douban','region'])
movie_info.index = movie_info.index + 1

print(movie_info.info())
print(movie_info.head(10))
fileName = "IMDBTop250vsDouban.csv"
movie_info.to_csv(fileName, sep=",", encoding = "utf-8", index=False)

