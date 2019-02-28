# -*- coding: utf-8 -*-

'''
    File name: HCP_identifier_scraper
    Author: Linfan Xiao
    Date created: 17/7/2018
    Date last modified: 18/7/2018
    Python Version: 3.6.1
'''

#############################################################
# Website to search from
url = "https://prs.moh.gov.sg/prs/internet/profSearch/main.action?hpe=SMC"

outputFileName = "E:\\Activities\\Professional\\2018 summer Abbott\\documents\\UnwieldyWellgroomedMedian\\SG_doctor_identifiers.csv"

# Set a pause time between searches (e.g., between 20 to 30s) to avoid bombarding the website with requests; the longer the pausing time, the more stable the progress. If the program encounters an "exist status -1" error, kindly increase the pause time. The doctorInfo are saved real-time.
pauseTime = [1,2]

#############################################################
import requests
import csv
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
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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

########################################################

# Set up output file
with open(outputFileName,'w', newline="", encoding='utf-8') as outputFile:
  colNames = ['Name', 'Registration Number']
  writer = csv.writer(outputFile)
  writer.writerow(colNames)

#########################################################
# Scrape doctor names and registration numbers
#########################################################
# Prepare to monitor the loop
startTime = time.time()
r = 1

#browser.set_page_load_timeout(30)
browser.get(url)
# switch to frame before locating search button
browser.switch_to.frame("msg_main")

#searchButton = browser.find_element_by_xpath('//*[@id="searchProf"]/div[2]/table/tbody/tr[3]/td/input[4]')
searchButton = browser.find_element_by_name("btnSearch")
searchButton.click()

# total number of doctors
searchResultText = browser.find_element_by_id("searchResultHead").text
m = int(re.findall('\d+', searchResultText)[1])
n = int(re.findall('\d+', searchResultText)[2])

# Scrape n/m pages, m doctors per page
pageNo = 1

while r < n:
  sleep(random.randint(pauseTime[0], pauseTime[1]))
  # Monitor the requests
  elapsedTime = time.time() - startTime
  remainingRequests = n - r
  print('Request: {}; Remaining: {}; Frequency: {} requests/s'.format(r, remainingRequests, r/elapsedTime))
  clear_output(wait = True)

  results = browser.find_elements_by_class_name('font15px')

  for result in results:
    resultText = result.text
    print(resultText)
    regNo = re.findall(r'M[A-Z]{0,}\d+[A-Z]{1}', resultText)[0]
    start = resultText.find(regNo)-2
    name = resultText[:start]
    #name = resultText.split('(M')[0].strip()
    #regNo = 'M' + resultText.split('(M')[1].strip().replace(")","")

    print("No. {}: {} {}".format(r, name, regNo))
    r += 1

    with open(outputFileName,'a', newline="", encoding='utf-8') as outputFile:
      writer = csv.writer(outputFile)
      row = [name, regNo]
      writer.writerow(row)
  
  # if web page malfunctions and reverts back to start page, jump to current page asap
  try:
    nextPageButton = browser.find_element_by_xpath(".//a[contains(@href, 'javascript:gotoPageDEFAULT(" + str(pageNo+1) + ")')]")
  except:
    browser.get(url)
    browser.switch_to.frame("msg_main")
    searchButton = browser.find_element_by_name("btnSearch")
    searchButton.click()
    # go to current page
    pageCount = 1
    while pageCount < pageNo:
      pageButtonList = browser.find_elements_by_xpath(".//a[contains(@href, 'javascript:gotoPageDEFAULT')]")
      pageList = []
      for x in pageButtonList:
        try:
            pageList.append(int(x.text))
        except:
            continue
      if pageNo in pageList:
        jumpToPageNo = pageNo
      else:
        jumpToPageNo = max(pageList)
      
      jumpToPageButton = browser.find_element_by_xpath(".//a[contains(@href, 'javascript:gotoPageDEFAULT(" + str(jumpToPageNo) + ")')]")
      pageCount = jumpToPageNo
      jumpToPageButton.click()


  pageNo += 1
  nextPageButton = browser.find_element_by_xpath(".//a[contains(@href, 'javascript:gotoPageDEFAULT(" + str(pageNo) + ")')]")
  nextPageButton.click()