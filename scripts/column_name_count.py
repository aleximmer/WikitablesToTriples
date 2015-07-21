import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import csv, json
from wikitables.page import Page
from collections import defaultdict

data = json.load(open('/Users/williraschkowski/Developer/wiki-list_of-retrieval/scripts/data/names.json', 'r'))
pages = data['pages']
tables = data['tables']
rows = list(csv.reader(open('/Users/williraschkowski/Developer/wiki-list_of-retrieval/scripts/data/TitlesShuffled.csv', 'r')))

print("Continuing at row %d ('%s')" % (pages, rows[pages][0]))

name_count = defaultdict(int)
for key, value in data['names'].items():
    name_count[key] = value

for row in rows[pages:]:
    print(row[0])
    try:
        page = Page(row[0])
        page.tables
    except Exception:
        pages += 1
        continue
    for table in page.tables:
        for name in table.columnNames:
            name_count[name] += 1
        tables += 1
    pages += 1

    json.dump({'pages': pages, 'tables': tables, 'names': name_count},
              open('/Users/williraschkowski/Developer/wiki-list_of-retrieval/scripts/data/names.json', 'w'),
              indent=2,
              ensure_ascii=False)
