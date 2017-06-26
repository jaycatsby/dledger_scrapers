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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

MAIN_URL = 'http://kresge.org/grants'
DL_ORGS = os.path.join(os.pardir+'/ledger-db','organizations.csv')
DL_GRANTS = os.path.join(os.pardir+'/ledger-db','grants.csv')

def init_driver(*args, **kwargs):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
        "(KHTML, like Gecko) Chrome/15.0.87"
    )
    driver = webdriver.Chrome() ### To use GUI Web Driver through Google Chrome
    # driver = webdriver.PhantomJS()
    driver.set_window_size(1400,1000)
    driver.get("http://kresge.org/grants?f[0]=field_programs%3A1297")
    return driver ### Returns the main landing page for the offender search form with Search by GDC ID displayed

def kresgeDetails(grants_page):
    grants_driver =webdriver.Chrome()
    # grants_driver = webdriver.PhantomJS()
    grants_driver.set_window_size(1400,1000)
    grants_driver.get(grants_page) # Opens a new webdriver object for grant's profile page
    grants_body = grants_driver.find_element_by_class_name('field-type-text-with-summary')
    grants_description = grants_body.find_element_by_tag_name('p').text
    sys.stdout.write("Finished retrieving grant's description....\n")
    sys.stdout.flush()
    grants_driver.close()
    return grants_description

def convertNumeric(val):
    converter = {
        'thousand':1000, 'k':1000,
        'million':1000000, 'm':1000000,
        'billion':1000000000, 'b':1000000000
    }
    unit = val.split(' ')[1]
    number = val.split(' ')[0]
    return converter[unit] * float(number)

def scrapeKresge(sel_driver, count=0, page=0):
    prev_count = count
    page += 1
    output = list()
    org_rows = sel_driver.find_elements_by_class_name('views-row')
    for org_row in org_rows: # org_rows[:1] to test with just first row
        try:
            org_details = dict()
            org_name = org_row.find_element_by_class_name('field-name-field-organization')
            sys.stdout.write('Found row data for {}...\n'.format(org_name.text))
            sys.stdout.flush()
            sys.stdout.write('Scraping grant awarded to {}...\n'.format(org_name.text))
            sys.stdout.flush()

            grants_url = org_name.find_element_by_tag_name('a').get_attribute('href')
            grants_year = int(re.sub('[a-zA-Z\:]','', org_row.find_element_by_class_name('date-display-single').text))
            try:
                grants_received = int(re.sub('[\$,]', '',org_row.find_element_by_class_name('field-name-field-grantamount').text))
            except ValueError: # For handling '$x.x million'
                grants_received = convertNumeric(re.sub('[\$,]', '',org_row.find_element_by_class_name('field-name-field-grantamount').text))

            address = org_row.find_element_by_class_name('field-name-field-location').text
            description = kresgeDetails(grants_url)

            org_details = {
                'granter_id': '', # To get with a func
                'grantee': org_name.text,
                'grantee_id': '', # To get with a func
                'amount': grants_received, # Mainly for organizations.csv format
                'grants_year': grants_year, # Starting from here is for <Add Grant> fields
                'address': address, # currently retrieving only 'Detroit, Mich.'
                'description': description,
                'url': grants_url
            }
            output.append(org_details)
        except:
            sys.stdout.write('Unknown Error with grant... Moving on....\n')
            sys.stdout.flush()

    new_count = prev_count + len(output)
    sys.stdout.write('Saving page {} to <kresge.csv>...\n'.format(page))
    sys.stdout.flush()

    lst_ind = 0
    for i in range(prev_count,new_count):
        csvKresge(output[lst_ind],i)
        lst_ind += 1

    try:
        sel_driver.find_element_by_class_name('pager__link--next').click()
        # WebDriverWait(sel_driver, 5).until(EC.presence_of_element_located((By.ID,'views-row')))
        sys.stdout.write('Moving on to page {}...\n'.format(page+1))
        sys.stdout.flush()
        return scrapeKresge(sel_driver, new_count, page)
    except:
        print('\n\nRetrieved {} grants from <kresge.org/grants?f[0]=field_programs%3A1297>'.format(new_count))
        return output

def csvKresge(data_entry,entry_num):
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
    if not os.path.isfile('kresge.csv'):
        init_df = pd.DataFrame(columns=DATA_COLS)
        init_df.to_csv('kresge.csv', index_label='#', header=DATA_COLS)
        sys.stdout.write('Initialized <kresge.csv>...\n')
        sys.stdout.flush()
    # for data_entry in data_lst:
    data_dict = {
        'start': '01/01/{}'.format(data_entry['grants_year']), # If the website doesn't specify start or end
        'end': '12/31/{}'.format(data_entry['grants_year']),
        'granter_id': data_entry['granter_id'],
        'grantee': data_entry['grantee'],
        'grantee_id': data_entry['grantee_id'],
        'url': data_entry['url'],
        'amount': data_entry['amount'],
        'description': data_entry['description']
    }
    with open('kresge.csv','a') as csv_output:
        data_df = pd.DataFrame(data_dict, index=[entry_num], columns=DATA_COLS)
        data_df.to_csv(csv_output, header=False)


def csvOrgs(): # For Updating Database Numbers
    org_data = list()
    if os.path.isfile(DL_ORGS):
        with open(DL_ORGS, 'rb') as ledger_csv:
            org_df = pd.read_csv(ledger_csv, skipinitialspace=True, usecols=['Id','Org_name']) # Can use additional columns by specifying in usecols
        return org_df
    else:
        print('Could not find <organizations.csv>....')
        print('Download from:\nhttps://www.detroitledger.org/#!/our-methods')
        return None

def csvGrants(funder_id):
    grants_data = list()
    if os.path.isfile(DL_GRANTS):
        with open(DL_GRANTS, 'rb') as ledger_csv:
            grants_df = pd.read_csv(ledger_csv, skipinitialspace=True, usecols=['to','from','Amount','Recipient ID','Funder ID','Start year','End year','Description'])
            for grants in grants_df:
                grants_data.append(grants_df.loc[grants_df['Funder ID']==funder_id])
        return grants_data
    else:
        print('Could not find <grants.csv>...')
        print('Download from:\nhttps://www.detroitledger.org/#!/our-methods')
        return None

def main():
   service_args = [
      '--proxy=127.0.0.1:9999',
      '--proxy-type=http',
      '--ignore-ssl-errors=true'
      ]
   # driver = init_driver(service_args=service_args)
   driver = init_driver()
   data_rows = scrapeKresge(driver)
   driver.close()

   # For loading DL's <organizations.csv>
   # ledgerOrgs = csvOrgs()
   # print(ledgerOrgs)

   # For loading DL's <grants.csv>
   # kresge_id = 308
   # ledgerGrants = csvGrants(kresge_id)
   # print(ledgerGrants)

main()
