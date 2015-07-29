from sparql import *
from page import Page
import os

"""Helper functions for evaluation and testing go here."""

def crawl_pages():
    f = open('titles2.txt', 'r', errors='ignore')
    titles = f.read()
    # FERTIG

crawl_pages()

def best_predicate_in_page(page, ignore=True):
    """Return predicate with highest relative occurance in page. Set 'ignore' to ignore '100%'."""

    columnPermutation = [p for table in page['tables'] for p in table['predicates']]

    predicates = [(key, value) for perm in columnPermutation for key, value in perm['predicates'].items()]

    if ignore:
        predicates = [p for p in predicates if not p[1] == 1.0]

    return max(predicates, key=lambda x: x[1]) if len(predicates) > 0 else (None, 0.0)

def best_predicate_in_table(table, ignore=True):
    """Return predicate with highest relative occurence in table. Set 'ignore' to ignore '100%'."""

    predicates = [(key, value) for p in table['predicates'] for key, value in p.items()]

    if ignore:
        predicates = [p for p in predicates if not p[1] == 1.0]

    return max(predicates, key=lambda x: x[1]) if len(predicates) > 0 else (None, 0.0)

def has_predicate(sub, obj, predicate):
    return predicate in predicates(sub, obj)

def load_pages(path):
    """This loads all .json-Files from path."""
    paths = [os.path.join(path,fn) for fn in next(os.walk(path))[2] if fn.endswith('.json')]
    pages = []
    for path in paths:
        try:
            page = json.load(open(path, 'r'))
        except ValueError:
            print('Couldn\'t load %s' % path)
        else:
            page['file'] = path.split('/')[-1]
            pages.append(page)
    return pages

def collect_tables(list_of_pages):
    tables = [table for page in list_of_pages for table in page['tables']]
    return [table for page in list_of_pages for table in page['tables']]

def collect_predicates(list_of_pages):
    # If you're a learner, have a look https://stackoverflow.com/questions/11264684/flatten-list-of-lists/11264751#answer-11264751
    return [(key, value) for table in collect_tables(list_of_pages) for p in table['predicates'] for key, value in p['predicates'].items()]

def collect_permutations(list_of_pages):
    return [p for t in collect_tables(list_of_pages) for p in t['predicates']]

def test_generate_RDFs(title, threshold=0.0):
    pg = Page(title)
    if not pg.tables:
        print('No tables contained')

    for table in pg.tables:
        table.generateRDFs(threshold)

def test_key_extraction(title='List of national parks of India'):
    pg = Page(title)
    if pg.tables:
        tb = pg.tables[0]
        print(tb.keyName)
    else:
        print('No tables contained')

def test_column_names(title, key):
    pg = Page(title)
    if not pg.tables:
        return
    tb = pg.tables[0]
    for column in tb.columnNames:
        if not column == key:
            print(column)
            print(tb.predicatesForColumns(key, column,))

def test_key_predicates(title):
    pg = Page(title)
    if not pg.tables:
        return
    tb = pg.tables[0]
    print(tb.predicatesForKeyColumn())

def test_key_relative_predicates(title):
    pg = Page(title)
    if not pg.tables:
        return
    tb = pg.tables[0]
    print(tb.relPredicatesForKeyColumn())

def test_generate_RDFsForKey(title):
    pg = Page(title)
    if not pg.tables:
        return
    tb = pg.tables[0]
    tb.generateRDFsForKey()
