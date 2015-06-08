import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import csv
import json
from random import randint
from wikitables import Table, Page
import os

with open('/Users/williraschkowski/Developer/knowledge-miners/scripts/TitlesShuffled.csv', 'r') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        try:
            page = (Page(row[0]))
            for i, table in enumerate(page.tables):
                path = '/Users/williraschkowski/Developer/knowledge-miners/scripts/testdata/%s %d.json' \
                    % (page.title.replace('/','-'), i)
                with open(path, 'w') as f:
                    json.dump(table.asDictionary(text=True), f)
                print(page.title)
        except Exception:
            continue
