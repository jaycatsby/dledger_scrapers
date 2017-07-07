# Detroit Ledger - Grant Scrapers
For retrieving grant data from websites of private foundations in Detroit. Currently, there are three projects: a scraper for [Ford Foundation](https://www.fordfoundation.org/work/our-grants/grants-database/grants-all), [Kresge Foundation](http://kresge.org/grants), and [Blue Cross Blue Shield of Michigan (BCBSM)](http://www.bcbsm.com/foundation/grant-programs/overview.html). Since Ford Foundation allows downloadable CSVs, the scraper bot for Ford focuses on opening the CSV url of grants and filtering the list by checking whether the grantee is alreayd in Detroit Ledger's database, grantee's name has the word ``Detroit`` in it, and/or ``Detroit`` is listed under the grant's `` Benefiting Locations``. Alternatively, ``matcher-standalone.html`` can be used to sort out the matches. Meanwhile, scrapers for Kresge Foundation and BCBSM currently use a pre-selected search field url to specifically target grants with ``Detroit`` as their ``Program`` field, and ``2016`` as ``Year`` for BCBSM.


Organization | Year | Status
--- | --- | ---
*Carls Foundation* | 2012 | **ENTERED**
*Carls Foundation* | 2013 | **ENTERED**
*Carls Foundation* | 2014 | **ENTERED**
*Carls Foundation* | 2015 | **ENTERED**
*Chrysler Foundation* | 2014 | **ENTERED**
*C.S. Mott Foundation* | 2014 | **ENTERED**
*DTE Energy Foundation* | 2014 | **ENTERED**
*DTE Energy Foundation* | 2015 | **ENTERED**
*Ethel and James Flinn Foundation* | 2014 | **ENTERED**
*Ford Foundation* | 2014 | **SCRAPED & ENTERED**
*Ford Foundation* | 2015 | **SCRAPED**
*Ford Foundation* | 2016 | **SCRAPED**
*Ford Foundation* | 2017 | **SCRAPED**
*Max M. & Marjorie S. Fisher Foundation* | 2015 | **ENTERED**
*Skillman Foundation* | 2014 | **ENTERED**
*Skillman Foundation* | 2015 | **ENTERED**
*William Davidson Foundation* | 2014 | **ENTERED**
*William Davidson Foundation* | 2015 | **ENTERED**

## Install
See requirements.txt for the full list of modules to run the program. There are only three modules to manually install in your Python virtual environment:
```
python3 -m venv .
```
```
(Linux) source bin/activate
(PC) source Scripts/activate
```
```
pip install r- /path/to/requirements.txt
```
Although this will install all the necessary modules to run bcbsm-scraper.py/kresge-scraper.py/ford-scraper.py, running the scraper for Kresge Foundation will require either [Chrome WebDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) or [PhantomJS WebDriver](http://phantomjs.org/download.html).
For using Chrome: uncomment Lines 30 & 37 in kresge-scraper.py, uncomment Line 26 in bcbsm-scraper.py
For using PhantomJS: uncomment Line 28 in kresge-scraper.py as well as Lines 22-26 for spoofing bot headers (same for bcbsm-scraper.py).

## Run
### Kresge Foundation
Line 33 in ``kresge-scraper.py`` directs the Selenium WebDriver to [Kresge Foundation's grant database](http://kresge.org/grants?f[0]=field_programs%3A1297) with the search field ``Program`` already pre-selected to ``Detroit``. Although ``def scrapeKresge()`` (Lines 58-114) is responsible for iterating through the list of table rows and recursively navigating pages to scrape grant data awarded by Kresge since 2009, the function ``def KresgeDetails()`` (Lines 36-46) is called at Line 80 to retrieve not only the ``url`` of the grant's "profile page", but also its full-length ``description`` by opening the "profile page" in a new WebDriver.
To scrape all the grants from Kresge Foundation with ``Detroit`` as their ``Program Field``:
```
python3 scrapers/kresge-scraper.py
```

### Blue Cross Blue Shield of Michigan
Line 18 in ``bcbsm-scraper.py`` points to the main url for displaying online tables of [BCBSM grants awarded](http://www.bcbsm.com/foundation/past-recipients/grants-awarded.html) in the past. Meanwhile, Line 30 can use ``xpath``, ``css``, or ``html tags`` to ``.click()`` and choose specific year of grants to display from 2014 to 2016.

On a different note, given that many of the grants awarded by BCBSM are to individual researchers with format (e.g.):
```
ResearchProgramAward
...
...
FirstName LastName, Title(s)
$xx,xxx
ResearchProject
AffiliatedInstitution, AffiliatedDepartment
```
where ``AffiliatedInstitution`` is typically an organization already captured in Detroit Ledger DB (e.g. Wayne State University), the function ``def cleanData()`` (Lines 33-58), as the name suggests, receives the above sets of data as a list. Then from Line 37 to 56, the format for ``description`` of grant recipients who were mentioned in ``Investigator Initiated Research Program``, ``Physician Investigator Research Award Program``, or ``Student Award Program`` becomes ``FirstName LastName, Title(s) {at} AffiliatedInstitution, AffiliatedDepartment {for} ResearchProject``.

Aside from this cleaning portion, both ``granter_id`` and ``start/end`` are hardcoded for BCBSM and 2016, respectively. Finally, in the function ``def scrapeBCBSM()``, ``Lines 62-66`` are important for targeting the list of common HTML elements. So in the case that BCBSM redesigns their website layout for grants awarded page, these lines should change accordingly.

To scrape all the ``2016`` grants from BCBSM and locally create a CSV formatted for Detroit Ledger Schema:
```
python3 scrapers/bcbsm-scraper.py
```

### Ford Foundation
Line 22 in ``ford-scraper.py`` points to the [CSV download url](https://fordsubjectgrants.azurewebsites.net/v1/grants/search-csv?&MinAmount=0&MaxAmount=30000000&FiscalYearStart=2006&FiscalYearEnd=2017&Search&SortBy=1&SortDirection=0&IsBuild=) for list of grants awarded by Ford Foundation from 2006 to 2017. As of June 28, 2017, there were ``16,673`` retrieved from the downloaded CSV file. Similar to my approach for Kresge Foundation above, the ``download url `` I used already applied ``2006`` and ``2017`` to the ``FiscalYearStart`` and ``FiscalYearEnd`` search fields on the Ford Foundation [grant website](https://www.fordfoundation.org/work/our-grants/grants-database/grants-all).

In ``def getFordCSVGrants()`` (Lines 34-70), the commented out ``if`` statements between Lines 41-48 was where I experimented with 4 different methods to compile the most comprehensive list of Detroit-based grants:
- If ``Detroit`` is in CSV's`` Benefiting Locations`` (returned 253 results)
- If ``Detroit`` is in CSV's `` Grantee`` name (returned 53 results)
- If CSV's`` Grantee`` name is already in [Detroit Ledger DB](https://data.detroitledger.org/sites/default/files/organizations.csv) () (returned 383 results)
- All of the above (returned 582 results incl. one with ``nan`` value)

To scrape grants awarded by Ford Foundation from 2006 to 2017 and to locally save a filtered CSV file for Detroit Ledger Schema:
```
python3 scrpaers/ford-scraper.py
```


## Developing
### ford-scraper.py
- ``grantee_id`` is missing in the CSV output:
  * Either use ``matcher-standalone.html``,
  * Or use the list of dictionaries ``csv_orgs`` (Line 85)

### Auto-Updater
- Essentially set certain range of dates for the scrapers to run by themselves on a server?
- Python's built-in module ``time``

### Year as Parameter
- Currently, both scrapers use urls from pre-selected search fields (especially Lines 83-84 in ``bcbsm-scraper.py``)
  * Ask for a prompt asking Year for each scrapers
  * This could be expanded to other fields such as location, grant types



## Results
### kresge-scraper.py
See the [Google Doc](https://docs.google.com/document/d/1tJ66xI3HJXqKtJv-YNIxpeKRwGVJrQxn-N3NlbUSVjA/edit?usp=sharing)

### bcbsm-scraper.py
This was purely for making data retrieval and entry more efficient for Detroit Ledger as to include individual research grant data

## Troubleshooting
- Note(s) for ``kresge-scraper.py``:
  * [CSV Output] Although number of grants matched up for year 2014 between the online database and IRS Form 990, there may be more refined method of finding list of relevant grant data
- Note(s) for ``ford-scraper.py``:
  * [CSV Download URL] For some reason, all the column headers have a blank before label (e.g. `` ColumnName``). This is why I intentionally included the empty spaces in Line 39 while reading in the CSV as ``pandas DataFrame`` object.
