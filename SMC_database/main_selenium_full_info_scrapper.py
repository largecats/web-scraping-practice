# -*- coding: utf-8 -*-

'''
    File name: HCP_full_info_scraper
    Author: Linfan Xiao
    Date created: 17/7/2018
    Date last modified: 25/7/2018
    Python Version: 3.6.1
'''

#############################################################
# Website to search from
url = "https://prs.moh.gov.sg/prs/internet/profSearch/main.action?hpe=SMC"

inputFileName = "E:\\Activities\\Professional\\2018 summer Abbott\\documents\\UnwieldyWellgroomedMedian\\SG_doctor_identifiers.csv"
outputFileName = "E:\\Activities\\Professional\\2018 summer Abbott\\documents\\UnwieldyWellgroomedMedian\\SG_doctor_database.csv"

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
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

chromedriver = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver

#options=webdriver.ChromeOptions()
options = Options()
# prefs={  
#      'profile.default_content_setting_values': {  
#         'images': 2 
#     }  
# }  
# options.add_experimental_option('prefs',prefs)  

options.add_argument("--lang=en")

browser = webdriver.Chrome(chromedriver, chrome_options=options)

def read_csv_into_list(fileName):
  data = []
  with open(fileName, 'r') as f:
    # deal with comma in cells
    data = list(csv.reader(f, delimiter=","))
    '''
    for row in f:
      #row = (row.strip('\n')).split(',')
      data.append(row)
      #print(row)
    '''
  
  return data

########################################################

# Set up output file
with open(outputFileName,'w', newline="", encoding='utf-8') as outputFile:
  colNames = ['Name', 'Registration Number', 'Qualifications', 'Type of first registration/date', 'Type of current registration/date', 'Practising Certificate Start Date', 'Practising Certificate End Date', 'Entry date into Register of Family Physicians', 'Specialty/Entry date into the Register of Specialists','Department/Name of Practice Place', 'Address of Place of Practice', 'Tel', 'Google map place name', 'Google map address', 'Restrictions/Conditions', 'Date Imposed']
  writer = csv.writer(outputFile)
  writer.writerow(colNames)

#########################################################

class customException(Exception):
  pass

#########################################################
# define search function
#########################################################
# wait for element to become visible
wait = WebDriverWait(browser, 2)

def search(item):
  sleep(random.uniform(0.1,1))
  browser.get(url)
  # switch to frame before locating anything
  browser.switch_to.frame("msg_main")

  name, regNo = item[0], item[1]

  expandButton = browser.find_element_by_xpath(".//a[contains(@onclick, 'toggleSearchOptions()')]")
  expandButton.click()
  regNoSearchBox = browser.find_element_by_name('psearchParamVO.regNo')
  regNoSearchBox.clear()
  regNoSearchBox.send_keys(regNo)
  searchButton = browser.find_element_by_name("btnSearch")
  searchButton.click()

  searchResultText = browser.find_element_by_id("searchResultHead").text
  # if result not found, raise error
  if 'No records found' in searchResultText:
    print('No records found')
    raise customException('No records found')

  doctorLink = browser.find_element_by_xpath(".//a[contains(@onclick, 'viewMoreDetails')]")
  sleep(random.uniform(0.1,1))
  doctorLink.click()
  
  tableHead = browser.find_element_by_class_name("table-head").text
  regNoFound = re.findall(r'M[A-Z]{0,}\d+[A-Z]{1}', tableHead)[0]
  start = tableHead.find(regNo)-2
  nameFound = tableHead[:start]
  # nameFound = tableHead.split('(')[0].strip()
  # regNoFound = tableHead.split('(')[1].strip().replace(")","")
  # don't assert name is the same because of possible utf-8 encoding errors
  # assert name == nameFound
  assert regNo == regNoFound

  doctorInfo = []
  infoHeader = browser.find_elements_by_xpath("//*[@class='no-border table-title']")
  infoList = browser.find_elements_by_xpath("//*[@class='no-border table-data']")
  assert len(infoHeader) == len(infoList)

  workPlaceInfoList = []
  specialtyList = []
  restrictionsInfoList = []
  for i in range(len(infoHeader)):
    # find basic info
    title = infoHeader[i].text
    if title != "":
      s = infoList[i].text
      s = s.replace('\n'," ").strip()
    if title != "Map" and title != "":
      if title in ["Department / Name of Practice Place", "Address of Place of Practice", "Tel"]:
        workPlaceInfoList.append(s)
      elif title in ["Specialty / Entry date into the Register of Specialists", "Sub-Specialty / Entry date into the Register of Specialists"]:
        specialtyList.append(s)
      elif title in ["Restrictions", "Conditions", "Date Imposed"]:
        restrictionsInfoList.append(s)
      else:
        doctorInfo.append(s)
  
  doctorInfo = [name] + doctorInfo
  
  workPlaceFullInfoList = []
  # find all workplaces
  workPlaces = browser.find_elements_by_xpath(".//a[contains(@onclick, 'openGoogleMap')]")
  if len(workPlaces) == 0:
    workPlaceFullInfoList = [['']*5]
  else:
    # stores the index of work place
    noOfWorkPlacesFound = 0
    while noOfWorkPlacesFound < len(workPlaces):
      # if this is not the primary work place, need to search from the start page again, as going back to the main tab after closing the map tab results in stale element error
      if noOfWorkPlacesFound != 0:
        sleep(random.uniform(0.1,1))
        browser.get(url)
        # switch to frame before locating anything
        browser.switch_to.frame("msg_main")

        name, regNo = item[0], item[1]

        expandButton = browser.find_element_by_xpath(".//a[contains(@onclick, 'toggleSearchOptions()')]")
        expandButton.click()
        regNoSearchBox = browser.find_element_by_name('psearchParamVO.regNo')
        regNoSearchBox.clear()
        regNoSearchBox.send_keys(regNo)
        searchButton = browser.find_element_by_name("btnSearch")
        searchButton.click()

        doctorLink = browser.find_element_by_xpath(".//a[contains(@onclick, 'viewMoreDetails')]")
        sleep(random.randint(pauseTime[0], pauseTime[1]))
        doctorLink.click()

      # if this is the primary work place, directly locate all work places in page
      workPlaceLinkList = browser.find_elements_by_xpath(".//a[contains(@onclick, 'openGoogleMap')]")
      currentWorkPlaceLink = workPlaceLinkList[noOfWorkPlacesFound]
      currentWorkPlaceLink.click()

      # go to the new tab lastly opened
      tabList = browser.window_handles
      browser.switch_to.window(tabList[-1])

      try:
        wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "place-name")))
        placeName = browser.find_element_by_class_name('place-name').text
      except:
        placeName = ""
      
      try:
        wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "address")))
        address = browser.find_element_by_class_name('address').text
      except:
        address = ""
      
      workPlaceFullInfoList.append(workPlaceInfoList[noOfWorkPlacesFound*3:noOfWorkPlacesFound*3+3] + [placeName, address])
      noOfWorkPlacesFound += 1
      # close map tab
      browser.close()
      # go back to main tab
      tabList = browser.window_handles
      browser.switch_to.window(tabList[0])
  
  print(specialtyList)
  print(workPlaceFullInfoList)
  for specialty in specialtyList:
    for workPlace in workPlaceFullInfoList:
      with open(outputFileName,'a', newline="", encoding='utf-8') as outputFile:
        writer = csv.writer(outputFile)
        newRow = doctorInfo + [specialty] + workPlace + restrictionsInfoList
        print(newRow)
        writer.writerow(newRow)

#########################################################
# Search for doctor info & handle error recursively
#########################################################
def searchDoctor(doctorIdentifierList):
  for i in range(len(doctorIdentifierList)):
    try:
      search(doctorIdentifierList[i])
    except customException:
      searchDoctor(doctorIdentifierList[i+1:])
    except:
      searchDoctor(doctorIdentifierList[i:])

#doctorIdentifierList = [['Anantham Devanand', 'M08698C']]
#doctorIdentifierList = [['ABHILASH BALAKRISHNAN', 'M01908I']]
#doctorIdentifierList = [['AMIT KANSAL', 'M19488C']]
#doctorIdentifierList = [['MARIA ISABEL SISON CABAÑERO', 'M64138C']]
doctorIdentifierList = [['CHEUNG NING', 'M60259J']]
#doctorIdentifierList = read_csv_into_list(inputFileName)
# discard headers
#doctorIdentifierList.pop(0)
searchDoctor(doctorIdentifierList)