# from bs4 import BeautifulSoup
# import requests
### The modules above are not necessary since CSV can be downloaded from <https://www.fordfoundation.org/work/our-grants/grants-database/grants-all>

import pandas as pd
import numpy as np
import sys
import os

MASTER_CSV = os.path.join(os.pardir+'/ledger-db','organizations.csv')

def loadMasterCSV():
    org_names = list()
    with open(MASTER_CSV, 'rb') as ledger_csv:
        master_df = pd.read_csv(ledger_csv)
        ledger_orgs = master_df['Org_name'].tolist()
        for orgs in ledger_orgs:
            org_names.append(orgs.encode('utf-8')) ### Otherwise Python gets angry with UnicodeErrors...
    return org_names

def loadFordCSV(year, master_lst):
    FORD_CSV = os.path.join(os.pardir+'/ledger-db','ford-{}.csv'.format(year)) ### The CSV was downloaded from <https://www.fordfoundation.org/work/our-grants/grants-database/grants-all?minyear=2006&maxyear=2017&page=0>
    relevant_grants = list()
    with open(FORD_CSV, 'rb') as ford_grants:
        ford_df = pd.read_csv(ford_grants)
        grantees = ford_df['Grantee'].tolist()
        for grantee in grantees:
            if grantee.encode('utf-8') in master_lst: ### Had to encode the list in <organizations.csv>...
                relevant_grants.append(ford_df.loc[ford_df['Grantee']==grantee])
    return relevant_grants ### Returns a list of <pandas DataFrame objs>



def main(yr):
    extant_orgs = loadMasterCSV()
    ford_grants = loadFordCSV(yr, extant_orgs)
    print(ford_grants[:10])

main(2017)
