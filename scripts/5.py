import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from bs4 import BeautifulSoup
import json, csv
import wikitables as w
from wikitables import Table, Page
from helper import *

savePath = './testdata/%s.json'
with open('./TitlesShuffled.csv', 'r') as f:
    titles = csv.reader(f)
    count = 0

    for title in titles:
        try:
            page = w.Page(title)
        except Exception:
            continue

        with open(savePath % page.title.replace('/', '\\'), 'w') as f:
            json.dump(page.predicates(relative=True, omit=True), f)

        count += 1
        if count == 1:
            notify(count, 'willi@raschkowski.com', 'PASSWORD')
            exit()
