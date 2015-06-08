import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import csv
from random import randint
from wikitables import Table, Page

tables = 0
skipped = 0

with open('/Users/williraschkowski/Developer/knowledge-miners/scripts/tablePages.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        page = row
