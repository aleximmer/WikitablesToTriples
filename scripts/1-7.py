import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from bs4 import BeautifulSoup
import json, csv
import wikitables as w
from wikitables.tests import *
from wikitables.sparql import *
from wikitables import Table, Page
from helper import *
from rdflib import Namespace, Graph

files = []
with open('/Users/williraschkowski/Developer/wiki-list_of-retrieval/scripts/data/good_titles.txt', 'r') as f:
    reader = csv.reader(f)
    for title, file in reader:
        files.append(file)

for count, file in enumerate(files):
    if os.path.exists('/Users/williraschkowski/Developer/wiki-list_of-retrieval/scripts/data/triples/%s' % file.replace('json', 'csv')):
        continue
    with open('/Users/williraschkowski/Developer/wiki-list_of-retrieval/scripts/testdata/' + file) as f:
        data = json.load(f)
        page = Page(data['page'])

        with open('/Users/williraschkowski/Developer/wiki-list_of-retrieval/scripts/data/triples/%s' % file.replace('json', 'csv'), 'w', encoding="utf-8") as rdfFile:
            writer = csv.DictWriter(rdfFile, fieldnames=['subject', 'predicate', 'object', 'certainty', 'page'])
            for i, pageTable in enumerate([table for table in page.tables if not table.skip()]):
                dataTable = data['tables'][i]
                for permutation in dataTable['predicates']:
                    sub = pageTable.column(permutation['subject'], content=True)
                    obj = pageTable.column(permutation['object'], content=True)
                    for i, _ in enumerate(sub):
                        if not isResource(sub[i]):
                            continue

                        for predicate, certainty in permutation['predicates'].items():
                            if not predicateExists(sub[i], predicate, obj[i]):
                                writer.writerow({
                                    'subject': sub[i],
                                    'predicate': predicate,
                                    'object': obj[i],
                                    'certainty': certainty,
                                    'page': data['page']
                                })
    print(count)
