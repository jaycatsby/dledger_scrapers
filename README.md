# Grant Scrapers
For retrieving grant data from websites of private foundations in Detroit. Currently, there are two projects in development: a scraper for [Ford Foundation](https://www.fordfoundation.org/work/our-grants/grants-database/grants-all) and another one for [Kresge Foundation](http://kresge.org/grants). Since Ford Foundation allows downloadable CSVs, the scraper bot for Ford focuses on opening locally stored CSV of grants and filtering through that list. Meanwhile, scraper for Kresge Foundation currently uses a pre-selected search field url to specifically target grants with 'Detroit' as their 'Program' field.

## Install
See requirements.text for the full list of modules to run the program. There are only three modules to manually install in your Python virtual environment:
```
pip install r- /path/to/requirements.text
```

## Run
