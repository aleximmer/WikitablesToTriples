import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from bs4 import BeautifulSoup
import json
import wikitables as w
from wikitables import Table, Page
from helper import *

titles = [
    'List of people named Jesse',
    'List of Super Bowl winning Head Coaches',
    'List of images and subjects in Gray\'s Anatomy: X. The Organs of the senses and the Common integument',
    'List of Swiss Inventions',
    'List of Greeks in Thrace',
    'List of 10 Items or Less episodes',
    'List of towns in Ourense',
    'List of Alsace-Lorraine locomotives',
    'List of asteroids/95101\u201395200',
    'List of Old Collegians of PLC Melbourne',
    'List of King George V Playing Fields in West Lothian',
    'List of shipwrecks in September 1940',
    'List of federal presidents of Austria',
    'List of communes of the Alpes-Maritimes departement',
    'List of listed buildings in Kintail, Highland',
    'List of cocktails with everclear',
    'List of settlements in the Federation of Bosnia and Herzegovina/R',
    'List of Lepidoptera that feed on eucalyptus',
    'List of butterflies of Christmas Island',
    'List of WNBC personalities',
    'List of ships in the Matrix series',
    'List of Amusement Parks',
    'List of Intel Pentium III microprocessors',
    'List of Top 25 albums for 1965 in Australia',
    'List of photo-sharing websites',
    'List of FBI Directors',
    'List of SOE agents',
    'List of hospitals in North Carolina'
]

page = w.Page(titles[27])
print(page)

with open('./result.json', 'w') as f:
    json.dump(page.predicates(relative=True, omit=True), f)
