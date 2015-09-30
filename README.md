# Extracting knowledge from tables in List_of pages in Wikipedia
.. image:: https://travis-ci.org/AlexImmer/WikitablesToTriples.svg?branch=master
  :https://travis-ci.org/AlexImmer/WikitablesToTriples

### Installation

**clone repo**
**install required packages [requirements.txt](https://github.com/AlexImmer/wiki-list_of-retrieval/blob/master/requirements.txt)**

### Repository Structure

**The Module 'Wikitables'**

```
/wikitables                -- module to retrieve data
  |-page.py                -- wiki-pages module respecting tables
  |-sparql.py              -- sparql connection to get required data
  |-table.py               -- wikitable module for information extraction
  |-keyExtractor.py        -- list of methods used to extract the key of a table
/tests                     -- testing modules
|-requirements.txt         -- python packages required
```
