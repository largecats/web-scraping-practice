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

##################################################
#                   main loop                    #
##################################################
# set working directory
path = ""
os.chdir(path)

# scrape 10 pages, 25 movies per page
pages = [str(i) for i in range(0,10)]

# declare lists to store data
names = []
years = []
genres = []
imdbRatings = []
doubanRatings = []
regions = []

# for every page
for page in pages:

    # make request
    url = "https://movie.douban.com/top250?start=" + str(int(page)*25) + "&filter="
    print(url)
    response = requests.get(url)

    # pause loop to avoid bombarding the site with requests
    sleep(random.randint(3, 5))

    # parse page
    pageHtml = BeautifulSoup(response.text, 'html.parser')

    # select all the 50 movie containers from a single page
    movieContainers = pageHtml.find_all('div', class_ = 'item')

    # for every one of these 25 containers in a page
    for container in movieContainers:

        movieInfo = container.find('div', class_="hd")

        # enter douban movie page
        movieUrl = movieInfo.a.get('href')
        doubanMoviePage = requests.get(movieUrl)
        # if the movie does not have a douban page, move on to the text one
        if "页面不存在" in doubanMoviePage.text:
        	continue
        doubanMoviePageHtml = BeautifulSoup(doubanMoviePage.text, "lxml")

        # scrape year
        year = (doubanMoviePageHtml.find("span", class_ = "year")).text
        pattern = re.compile(r'(\d{4})', flags=re.DOTALL)
        year = (pattern.findall(year))[0]
        years.append(year)

        # scrape douban rating
        doubanRating = float((doubanMoviePageHtml.find("strong", class_="ll rating_num")).text)
        doubanRatings.append(doubanRating)

        # ender imdb movie page from douban
        basic_info = doubanMoviePageHtml.find("div", attrs={"id":"info"})
        pattern = re.compile(r'IMDb链接: tt(\d{7})', flags=re.DOTALL)
        imdb_id = pattern.findall(basic_info.text)[0]
        imdb_url = "http://www.imdb.com/title/tt" + imdb_id + "/"
        print(imdb_url)

        imdbMoviePage = requests.get(imdb_url)
        imdbMoviePageHtml = BeautifulSoup(imdbMoviePage.text, "lxml")

        # scrape genre
        pattern = re.compile(r'<span class="itemprop" itemprop="genre">(.+?)</span>', flags=re.DOTALL)
        genre = pattern.findall(imdbMoviePage.text)
        genre = ", ".join(genre)
        genres.append(genre)

        # scrape region
        details_info = imdbMoviePageHtml.select('div#titleDetails')[0]
        textBlocks = details_info.find_all('div', class_="txt-block")
        for t in textBlocks:
            if 'Country' in t.text:
                region_info = t
                break
        region = region_info.a.text
        regions.append(region)

        # scrape imdb rating
        pattern = re.compile(r'<span itemprop="ratingValue">(.+?)</span>', flags=re.DOTALL)
        imdbRating = float(pattern.findall(imdbMoviePage.text)[0])
        imdbRatings.append(imdbRating)

        # scrape (english) name
        name = imdbMoviePageHtml.find('h1').text
        name = name.rstrip()
        names.append(name)

        print(name, year, genre, imdbRating, doubanRating)

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
fileName = "DoubanTop250vsIMDB.csv"
movieInfo.to_csv(fileName, sep=",", encoding = "utf-8", index=False)