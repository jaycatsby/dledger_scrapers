import requests
import pandas as pd
import random
import time
import sys
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

MAIN_URL = 'http://www.bcbsm.com/foundation/past-recipients/grants-awarded.html'

def init_driver(*args, **kwargs):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
        "(KHTML, like Gecko) Chrome/15.0.87"
    )
    # driver = webdriver.Chrome() ### To use GUI Web Driver through Google Chrome
    driver = webdriver.PhantomJS()
    driver.set_window_size(1400,1000)
    driver.get(MAIN_URL)
    driver.find_element_by_xpath('//*[@id="contentBody4"]/div/div[3]/div/ul/li[1]/a').click() # To make sure we select the tab content for year 2016
    return driver

def cleanData(data_lst):
    export_lst = list()
    for data in data_lst:
        filtered_dict = dict()
        if data['program']=='Investigator Initiated Research Program' or data['program']=='Physician Investigator Research Award Program' or data['program']=='Student Award Program':
            filtered_dict = {
                'granter_id': data['granter_id'],
                'start': data['start'],
                'end': data['end'],
                'grantee': data['grantee'].split(',')[0],
                'amount': data['amount'],
                'description': '{} at {} for {}: {}'.format(data['grantee_detail'], data['grantee'], data['program'], data['description']),
                'url': data['url']
            }
        else:
            filtered_dict = {
                'granter_id': data['granter_id'],
                'start': data['start'],
                'end': data['end'],
                'grantee': data['grantee_detail'],
                'amount': data['amount'],
                'description': '{}: {}'.format(data['program'], data['description']),
                'url': data['url']
            }
        export_lst.append(filtered_dict)
    return export_lst

def scrapeBCBSM(sel_driver):
    bcbms_lst = list()
    bcbms_table = sel_driver.find_element_by_class_name('tab-content')
    bcbms_headers_obj = [bcbms_label for bcbms_label in bcbms_table.find_elements_by_class_name('pullQuoteContent') if len(bcbms_label.find_elements_by_tag_name('h2'))>0]
    bcbms_headers = [bcbms_head.text for bcbms_head in bcbms_headers_obj] # Stores ['Community Health Matching Grant Program', 'Investigator Initiated Research Program', 'Request for Proposal', 'Physician Investigator Research Award Program', 'Proposal Development Award ', 'Student Award Program']
    header_index = -1 # Each time the program finds h2 tag, this index will increment by 1
    bcbms_columns = [bcbms_data for bcbms_data in bcbms_table.find_elements_by_class_name('pullQuoteContent')]

    for bcbms_col in bcbms_columns:
        if len(bcbms_col.find_elements_by_tag_name('h2'))>0:
            header_index += 1

        bcbms_texts = [bcbms.text.split('\n') for bcbms in bcbms_col.find_elements_by_tag_name('p') if len(bcbms.find_elements_by_tag_name('u'))==0]
        for bcbms_text in bcbms_texts:
            # data_dict = dict()
            if len(bcbms_text)>0:
                data_dict = {
                    'granter_id': 4562, # Ledger ID for BCBSM
                    'grantee_detail': bcbms_text[0],
                    'amount': bcbms_text[1],
                    'description': bcbms_text[2],
                    'grantee': bcbms_text[3],
                    'url': MAIN_URL,
                    'start': '01/01/2016', # Since the MAIN_URL given is for 2016 data
                    'end': '12/31/2016',
                    'program': bcbms_headers[header_index]
                }
                bcbms_lst.append(data_dict)

    filtered_lst = cleanData(bcbms_lst)
    ind_range = range(len(filtered_lst))
    saveBCBSM(filtered_lst, ind_range)
    # print(filtered_lst,'\n')

def saveBCBSM(data_lst, index_lst):
    DATA_COLS = [
        'start',
        'end',
        'granter_id',
        'grantee',
        'grantee_id',
        'url', # AKA grants_url
        'amount',
        'description'
    ]
    if not os.path.isfile('bcbms.csv'):
        init_df = pd.DataFrame(columns=DATA_COLS)
        init_df.to_csv('bcbms.csv', index_label='#', header=DATA_COLS)

    for data in data_lst:
        with open('bcbms.csv','a') as output:
            data_df = pd.DataFrame(data, index=[index_lst], columns=DATA_COLS)
            data_df.to_csv(output, header=False)
    print('Done saving the scraped results')

def main():
   service_args = [
      '--proxy=127.0.0.1:9999',
      '--proxy-type=http',
      '--ignore-ssl-errors=true'
      ]
   driver = init_driver(service_args=service_args)
   # driver = init_driver()
   data_rows = scrapeBCBSM(driver)
   driver.close()


main()
