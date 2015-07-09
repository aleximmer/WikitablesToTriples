# Extracting knowledge from tables in List_of pages in Wikipedia
===================

### Installation

* **clone repo**
* **install required packages [requirements.txt](https://github.com/AlexImmer/wiki-list_of-retrieval/blob/master/requirements.txt)**


### Frontend and Testing

**To store data and evaluate results we use a django-backend /list_extraction**

```
# in /list_extraction

# create your local database and create a user
python manage.py migrate
python manage.py createsuperuser

# import Lists into your Database (dump of 1k lists)
python manage.py importListsAsHTML

# open your browser to see the data in admin-view
localhost:8000/admin

# to start the test-tool for the key-extraction
localhost:8000/Tables/KeyForm
```

### Repository Structure

**Modules created are in /wikitables**

```
/data                      -- WikiList-Data
  |-ListOf.txt             -- All ListOf-articles
  |-Titles.txt             -- Only their titles
  |-...
/list_extraction           -- Django backend
  /extensions  			   -- Extensions for extraction
  /list_extraction
  /Lists_to_RDFs		   -- App representing Lists, Tables, RDFs
  |-manage.py              -- django
/scripts				   -- test and research scripts
/wikitables                -- final module to retrieve data
  |-page.py                -- wiki-pages module respecting tables
  |-sparql.py              -- sparql connection to get required data
  |-table.py               -- wikitable module for information extraction
|-requirements.txt         -- python packages required
```
