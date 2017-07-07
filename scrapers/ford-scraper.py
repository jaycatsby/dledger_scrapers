import urllib.request as urq
import requests
import pandas as pd
import time
import json
import sys
import os
import re


def getLedgerAPIOrgs():
    request = urq.Request('https://data.detroitledger.org/api/1.0/orgs?')
    response_text = urq.urlopen(request).read().decode('utf8')
    response_json = json.loads(response_text)
    orgs_json = response_json['orgs']
    # print(orgs_json) # For sample output, see <sample_apiJSON.json>
    # print(len(orgs_json)) # Returns 100
    return orgs_json

def getLedgerCSVOrgs():
    output_lst = list()
    LEDGER_URL = 'https://data.detroitledger.org/sites/default/files/organizations.csv'
    master_df = pd.read_csv(LEDGER_URL)
    org_tuples = list(zip(master_df['Id'].tolist(), master_df['Org_name'].tolist()))
    for org_id, org_name in org_tuples:
        org_dict = {
            'grantee_id': int(org_id),
            'grantee': org_name.encode('utf-8') # without encoding, will get a UnicodeEncodeError
        }
        output_lst.append(org_dict)
    # print(len(output_lst)) # Returns 1570 organization tuples
    return output_lst # List of dictionaries

def getFordCSVGrants(ledger_orgs):
    output_lst = list()
    index_counter = 0
    FORD_URL = 'https://fordsubjectgrants.azurewebsites.net/v1/grants/search-csv?&MinAmount=0&MaxAmount=30000000&FiscalYearStart=2006&FiscalYearEnd=2017&Search&SortBy=1&SortDirection=0&IsBuild='
    ford_df = pd.read_csv(FORD_URL)
    grant_tuples = list(zip(ford_df[' Grantee'].tolist(), ford_df[' Description'].tolist(), ford_df[' Amount'].tolist(), ford_df[' Benefiting Locations'].tolist(), ford_df[' Fiscal Year'].tolist(), ford_df[' Start Date'].tolist(), ford_df[' End Date'].tolist()))
    for grantee, desc, amt, loc, fisc_yr, start_date, end_date in grant_tuples:
        # if 'detroit' in loc.lower() or grantee.encode('utf-8') in ledger_orgs:
            # output_lst.append(grantee) # Returns 582 grantees as of 07/05/2017
        # if 'detroit' in loc.lower():
            # output_lst.append(grantee) # Only using ' Benefiting Locations' yields only 253
        # if grantee.encode('utf-8') in ledger_orgs:
            # output_lst.append(grantee) # Only using Org_name yields 383
        # if 'detroit' in grantee.lower():
            # output_lst.append(grantee) # Only 53 if checking Org_name contains 'Detroit'
        try:
            if grantee.encode('utf-8') in [org['grantee'] for org in ledger_orgs] or 'Detroit' in grantee or 'Detroit' in desc or 'detroit' in loc.lower():
                grant_data = {
                    'granter_id': 225,
                    'grantee': grantee,
                    'grantee_id': '',
                    'fiscal_year': fisc_yr,
                    'description': desc,
                    'amount': int(re.sub('[\$,]', '', amt)),
                    'start': start_date,
                    'end': end_date,
                    'url': FORD_URL
                }
                index_counter += 1

                output_lst.append((index_counter, grant_data)) # Returns 581 which is 1 less than the first IF statment since TypeError is not counted here
            # if 'Detroit' in desc:
            #     output_lst.append(grantee) # Only 154 if checking 'Detroit' in Description
        except TypeError:
            sys.stdout.write('TypeError by Grantee <{}> with Description <{}>.,,\n'.format(grantee,desc))
            sys.stdout.flush()
    return output_lst

def saveFordGrants(grant_datas):
    CSV_COLS = ['granter_id', 'grantee', 'grantee_id', 'fiscal_year', 'description', 'amount', 'start', 'end', 'url']
    if not os.path.isfile('ford-2006-2017.csv'):
        init_df = pd.DataFrame(columns=CSV_COLS)
        init_df.to_csv('ford-2006-2017.csv', index_label='#', header=CSV_COLS)
    with open('ford-2006-2017.csv', 'a') as csv_output:
        for (index_count, grant_data) in grant_datas:
            data_df = pd.DataFrame(grant_data, index=[index_count], columns=CSV_COLS)
            data_df.to_csv(csv_output, header=False)


def main():
    # api_orgs = getLedgerAPIOrgs() # Returns 100
    csv_orgs = getLedgerCSVOrgs()
    ford_db = getFordCSVGrants(csv_orgs)
    saveFordGrants(ford_db)

main()
