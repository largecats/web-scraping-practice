#https://www.dataquest.io/blog/web-scraping-beautifulsoup/

import requests
from lxml import html
import re
import pandas as pd
import numpy as np
import time
import random
from bs4 import BeautifulSoup
#import urllib
from IPython.core.display import clear_output
from time import sleep
from random import randint
from warnings import warn
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import limit

'''
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

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
# 设置user-agent请求头
dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片
browser = webdriver.PhantomJS(desired_capabilities=dcap)


browser.set_page_load_timeout(30)

browser.get('https://movie.douban.com')
assert "豆瓣电影" in browser.title
'''


def searchMovies(keyword=None):
    url = 'https://api.douban.com/v2/movie/search'
    params = {'q':keyword}
    response = requests.get(url, params=params)
    return response

#client = limit.Limit(DoubanService(server=SERVER), 60, 9)

from translate import Translator
translator= Translator(from_lang = "zh", to_lang="en")

# Redeclaring the lists to store data in
names = []
years = []
genres = []
imdb_ratings = []
douban_ratings = []
regions = []


# Make a get request
response = requests.get("http://www.imdb.com/chart/top")

# Parse the content of the request with BeautifulSoup
page_html = BeautifulSoup(response.text, 'html.parser')

for i in range(0,250):

    sleep(randint(40,45))
    # scrape the name
    title_info = page_html.find_all('td', class_ = 'titleColumn')[i]
    name = title_info.a.text
    names.append(name)

    # scrape the year
    year = title_info.span.text
    pattern = re.compile(r'(\d{4})', flags=re.DOTALL)
    year = (pattern.findall(year))[0]
    years.append(year)

    # scrape the rating
    #rating_info = page_html.find_all('td', class_ = 'ratingColumn imdbRating')[i]
    #imdb_rating = float(rating_info.strong.text)
    #imdb_ratings.append(imdb_rating)

    # enter the imdb movie page
    imdbMovieUrl = 'http://www.imdb.com' + title_info.a.get('href')
    imdbMoviePage = requests.get(imdbMovieUrl)
    imdbMoviePage_html = BeautifulSoup(imdbMoviePage.text, 'html.parser')
    print(imdbMovieUrl)

    # scrape the rating
    pattern = re.compile(r'<span itemprop="ratingValue">(.+?)</span>', flags=re.DOTALL)
    imdb_rating = float(pattern.findall(imdbMoviePage.text)[0])
    imdb_ratings.append(imdb_rating)

    # scrape the genre
    pattern = re.compile(r'<span class="itemprop" itemprop="genre">(.+?)</span>', flags=re.DOTALL)
    genre = pattern.findall(imdbMoviePage.text)
    genre = ", ".join(genre)
    genres.append(genre)

    #scrape the region
    details_info = imdbMoviePage_html.select('div#titleDetails')[0]
    textBlocks = details_info.find_all('div', class_="txt-block")
    for t in textBlocks:
        if 'Country' in t.text:
            region_info = t
            break
    region = region_info.a.text
    regions.append(region)

    # search douban rating
    keywords = name + " " + year


    doubanResult = searchMovies(keywords).json()
    results = doubanResult['subjects']
    n = 0
    while n < len(results):
        print(n)
        result = results[n]
        if name == result['original_title'] or year == result['year']:
            douban_rating = float(result['rating']['average'])
            break
        else:
            n += 1
    print(n)
    if n == len(results):
        douban_rating = "NA"

    douban_ratings.append(douban_rating)

    print(keywords, genre, region, imdb_rating, douban_rating)

    '''
    elem = browser.find_element_by_name("search_text")  # find the searchbox element
    elem.clear()  # clear content in search box
    elem.send_keys(keywords)  # enter in search box
    elem.send_keys(Keys.RETURN)

    searchPage_html = BeautifulSoup(browser.page_source, "lxml")
    containers = searchPage_html.find_all('div', class_ = 'item-root')
    n = 0
    print(len(containers))
    while j < len(containers):
        print(i)
        first_container = containers[j]
        title_info = first_container.find('div', class_="title").text
        if name in title_info and year in title_info:
            douban_rating = float(first_container.find("span", class_ = "rating_nums").text)
            break
        else:
            j += 1
    print(j)
    if j == len(containers):
        douban_rating = "NA"
        #tr_region = "NA"
    douban_ratings.append(douban_rating)
    #regions.append(tr_region)
    '''



#browser.close()

movie_ratings = pd.DataFrame({'movie': names,
                              'year': list(map(int,years)),
                              'genre': genres,
                              'imdb': imdb_ratings,
                              'douban': douban_ratings,
                              'region': regions},
                              columns = ['movie','year','genre','imdb','douban','region'])
movie_ratings.index = movie_ratings.index + 1

print(movie_ratings.info())
print(movie_ratings.head(10))
fileName = "IMDBTop250vsDouban_movie_ratings.csv"
movie_ratings.to_csv(fileName, sep=",", encoding = "utf-8", index=False)

