import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import csv
from random import randint
from wikitables import Table, Page

pages = 0
tables = 0
skipped = 0

with open('/Users/williraschkowski/Developer/knowledge-miners/scripts/tablePages.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        pages += 1
        page = Page(row[0])
        tables += len(page.tables)
        skipped += len([t for t in page.tables if t.skipTable()])
        print("Pages: %s, Tables: %s, Skipped: %s" % (pages, tables, skipped))
