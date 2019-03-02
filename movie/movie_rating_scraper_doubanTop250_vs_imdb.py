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

from translate import Translator
translator= Translator(from_lang = "zh", to_lang="en")

def check_contain_chinese(check_str):
	for ch in check_str.decode('utf-8'):
		if u'\u4e00' <= ch <= u'\u9fff':
			return True
	return False

# Scrape 10 pages, 25 movies per page
pages = [str(i) for i in range(0,10)]

# Redeclaring the lists to store data in
names = []
years = []
genres = []
imdb_ratings = []
douban_ratings = []
regions = []

# Preparing the monitoring of the loop
start_time = time.time()
r = 0

# For every page in the interval 1-4
for page in pages:

    # Make a get request
    #response = get('http://www.imdb.com/search/title?release_date=' + year_url + 
    #'&sort=num_votes,desc&page=' + page, headers = headers)
    url = "https://movie.douban.com/top250?start=" + str(int(page)*25) + "&filter="
    print(url)
    response = requests.get(url)

    # Pause the loop
    sleep(random.randint(8,15))

    # Monitor the requests
    r += 1
    elapsed_time = time.time() - start_time
    print('Request:{}; Frequency: {} requests/s'.format(r, r/elapsed_time))
    clear_output(wait = True)

    # Throw a warning for non-200 status codes
    if response.status_code != 200:
        warnings.warn('Request: {}; Status code: {}'.format(r, response.status_code))

    # Break the loop if the number of requests is greater than expected
    if r > 250:
        warnings.warn('Number of requests was greater than expected.')  
        break 

    # Parse the content of the request with BeautifulSoup
    page_html = BeautifulSoup(response.text, 'html.parser')

    # Select all the 50 movie containers from a single page
    mv_containers = page_html.find_all('div', class_ = 'item')
    print(len(mv_containers))

    # For every movie of these 50 movies
    for container in mv_containers:

        movie_info = container.find('div', class_="hd")

        # scrape the name
        '''
        name_info = movie_info.a.text
        allNames = name_info.split("/")
        name = []
        for s in allNames:
            s = s.strip()
            if not check_contain_chinese(s.encode('utf-8')):
                name.append(s)
        if len(name) > 0:
        	names.append(name[0])
        else:
        	movie_name = allNames[0].strip()
        print(movie_name)
        '''

        # enter douban movie page
        movieUrl = movie_info.a.get('href')
        doubanMoviePage = requests.get(movieUrl)
        if "页面不存在" in doubanMoviePage.text:
        	continue
        doubanMoviePage_html = BeautifulSoup(doubanMoviePage.text, "lxml")

        # scrape the year
        year = (doubanMoviePage_html.find("span", class_ = "year")).text
        pattern = re.compile(r'(\d{4})', flags=re.DOTALL)
        year = (pattern.findall(year))[0]
        years.append(year)

        # Scrape the douban rating
        douban_rating = float((doubanMoviePage_html.find("strong", class_="ll rating_num")).text)
        douban_ratings.append(douban_rating)

        # Scrape the region
        '''
        pattern = re.compile(r'<span class="pl">制片国家/地区:</span>(.+?)<br/>', flags=re.DOTALL)
        region = pattern.findall(doubanMoviePage.text)[0]
        region = region.strip()
        l = region.split("/")
        new = []
        for item in l:
            translation = translator.translate(item)
            new.append(translation)
        tr_region = "/".join(new)
        regions.append(tr_region)
        '''

        # imdb url
        #pattern = re.compile(r'<span class = "pl">IMDb链接:</span><a href=(.+?) target="_blank"', flags=re.DOTALL)
        #href = (doubanMoviePage_html.find("a", attrs={"target": "_blank", "rel":"nofollow"}))
        #imdb_url = href['href']
        basic_info = doubanMoviePage_html.find("div", attrs={"id":"info"})
        pattern = re.compile(r'IMDb链接: tt(\d{7})', flags=re.DOTALL)
        imdb_id = pattern.findall(basic_info.text)[0]
        imdb_url = "http://www.imdb.com/title/tt" + imdb_id + "/"

        imdbMoviePage = requests.get(imdb_url)
        imdbMoviePage_html = BeautifulSoup(imdbMoviePage.text, "lxml")

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

        # scrape the IMDB rating
        pattern = re.compile(r'<span itemprop="ratingValue">(.+?)</span>', flags=re.DOTALL)
        imdb_rating = float(pattern.findall(imdbMoviePage.text)[0])
        imdb_ratings.append(imdb_rating)

        # scrape the English movie name
        eng_name = imdbMoviePage_html.find('h1').text
        eng_name = eng_name.rstrip()
        names.append(eng_name)

        print(eng_name, year, genre, imdb_rating, douban_rating)

print(len(names), len(list(map(int,years))), len(genres), len(imdb_ratings), len(douban_ratings), len(regions))
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
fileName = "DoubanTop250vsIMDB_movie_ratings.csv"
movie_ratings.to_csv(fileName, sep=",", encoding = "utf-8", index=False)
