from sparql import *
from table import Table
from page import Page
from bs4 import BeautifulSoup
import json

def extractOntologies(table):
    colOnts = []
    keyEnts = table.column(table.key) # Voller HTML Code zu jeder Zelle
    namesInfo = json.load(open('names.json').read())
    importantNames = namesInfo.names # Haeufig auftretende Spaltennamen
    print(importantNames)
    for colName in table.columnNames:
        print('Check column "'+colName+'":')
        """
            1.) Check if colName occurres in names.json (unequal: one letter)
                (No match -> cancel this colName)
            2.) Get Predicates of each entitity -> Find nearly equal predicate for colName
                (No match in ent -> next entity)
                (No match in all ent -> cancel this colName)
        """

        if len(colName) <= 1:
            colOnts.push({'.'+colName: None})
            continue

        colNameShorted = colName.strip().lower()
        colOcc = 0
        for impName, occCount in importantNames.items():
           shorted = impName.strip().lower()
           # "30" Hardgecoded -> In Abhaengigkeit von namesInfo.tables setzen
           if occCount > 30 and impName == colNameShorted:
               colOcc = occCount
               break

        if colOcc == 0:
            colOnts.push({'.'+colName: None})
            continue

        predicates = predicates(dbpEntry)
        predCount = {} # Predicate -> Count
        for ent in keyEnts:
           dbpEntry = cellContent(new BeautifulSoup(ent))
           for pred in predicates:
               pred = pred.lower()
"""TODO"""     print(pred)
               # Looking at predicates (how to check on key col name?)
               raise ValueError('Just checking until this code line')
               # Success:
               predCount[pred.key]++

        predCount = sorted(predCount.items(),key=function(item){return item[1]})
        if predCount[0][1] > len(table.rows)/3: # 33 percent min
            colOnts.append({colName: predCount[0][0] })
        else:
            colOnts.append({'.'+colName: None})

    print('Results:')
    print(colOnts)

# Testing code:
def test(title='List of national parks of India'):
    pg = Page(title)
    if pg.tables:
        tb = pg.tables[0]
        extractOntologies(tb)
    else:
        print('No tables contained')

test()
