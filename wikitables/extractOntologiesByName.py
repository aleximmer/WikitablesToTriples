from sparql import *
from table import Table
from page import Page
from bs4 import BeautifulSoup
import json
import codecs
from fuzzywuzzy import process
import re

"""
    Fix fucked up Windows Shell encoding -> Run in cmd:
        chcp 65001
        set PYTHONIOENCODING=utf-8
"""

def extractOntologies(table):
    colOnts = []
    keyEnts = table.column(table.key) # Voller HTML Code zu jeder Zelle
    with codecs.open('names.json','r',encoding='utf-8',errors='xmlcharrefreplace') as f:
        namesInfo = json.loads(f.read())
    importantNames = namesInfo['names']

    i = -1
    for colName in table.columnNames:
        print('\nCheck column "'+colName+'":')
        i += 1
        if i == table.key:
            print('Abort checking (is key column)')
            continue

        if len(colName) <= 1:
            colOnts.append({colName: None})
            print('Column name "'+colName+'" is too short (Length: '+len(colName)+')')
            continue

        prepColName = cleanupName(colName)

        suggestedName = process.extractOne(prepColName, list(importantNames.keys()))
        if (suggestedName[1] < 90):
            colOnts.append({colName: None})
            print('Column name "'+prepColName+'" doesnt appear in relevant names collection')
            continue
        colOcc = int(importantNames[suggestedName[0]])

        if colOcc < 5:
            colOnts.append({colName: None})
            print('Column name "'+prepColName+'" doesnt occurre often enough in relevant names collection ('+str(colOcc)+' times)')
            continue
        else:
            print('Occurres '+str(colOcc)+' times in '+str(namesInfo['tables'])+' tables')

        predCount = {} # Predicate -> Count
        for ent in keyEnts:
            dbpEntry = cellContent(ent)
            print('DBPedia entry: '+dbpEntry)
            entPredicates = predicates(dbpEntry)

            if len(entPredicates) == 0:
                print('Key column cell is not an entity')
                continue
            # String matching on column name and predicates
            suggestedPred = process.extractOne(prepColName, entPredicates)
            predName = suggestedPred[0]
            predRating = suggestedPred[1]
            if (predRating > 85):
                if not (predName in predCount):
                    predCount[predName] = 1
                else:
                    predCount[predName] += 1
            else:
                print('No predictions found (by textual evidence) -> Best one:'+predName +'('+str(predRating)+')')

        predCount = sorted(predCount.items(),key=getRightVal,reverse=True)
        print('Result set for column "'+prepColName+'": '+str(predCount)+'\n')

        if len(predCount) > 0 and predCount[0][1] > len(table.rows)/3: # occurence: min 33 percent of table rows
            colOnts.append({colName: predCount[0][0]})
        else:
            colOnts.append({colName: None})
            print('Column "'+predName+'" hasnt any prediction hits')

    print('Results:')
    print(colOnts)

def cleanupName(name):
    # No newlines
    prepName = name.replace('\n',' ')

    # No quote mark(footnote)
    regPattern = re.compile('\[[^\]]*\]')
    prepName = regPattern.sub('', prepName)

    # Remove dot from beginnning
    if prepName[:1] == '.':
        prepName = prepName[1:]

    # No brackets
    regPattern = re.compile('\([^\)]*\)')
    prepName = regPattern.sub('', prepName)

    # Only one space at one position
    regPattern = re.compile('[ ]+')
    prepName = regPattern.sub(' ', prepName)

    # Remove whitespaces from the left and right side
    prepName = prepName.strip()

    # Each word begins with an upper cased letter (the other one are lower cased)
    words = prepName.split(' ')
    for i in range(len(words)):
        words[i] = words[i][:1].upper() + words[i][1:].lower()
    prepName = ' '.join(words)

    return prepName

def getRightVal(item):
    return item[1]

def fixNamesJSON():
    with codecs.open('names.json','r',encoding='utf-8',errors='xmlcharrefreplace') as f:
        namesInfo = json.loads(f.read())
    names = namesInfo['names'] # Alle 6468 auftretenden Spaltennamen
    newNames = {}
    for name, occ in names.items():
        clName = cleanupName(name)
        if not (clName in newNames):
            newNames[clName] = occ
        else:
            newNames[clName] += occ
    # Group importantNames by removing symbols, numbers and newlines (e.g. County Seat, INCITS)
    # importantNames = importantNames
    namesInfo['names'] = newNames
    namesInfo['namesCount'] = len(newNames)
    with codecs.open('names.json','w',encoding='utf-8') as f:
        f.write(json.dumps(namesInfo, indent=4, sort_keys=True))

# Testing code:
def test(title='List of national parks of India'):
    pg = Page(title)
    if pg.tables:
        tb = pg.tables[0]
        #print('Key: ' + str(tb.key))
        extractOntologies(tb)
    else:
        print('No tables contained')

test("List of post-1692 Anglican parishes in the Province of Maryland")

"""
columnNames = ['Name', 'County seat\n[8]', 'INCITS\n[7]']

with codecs.open('names.json','r',encoding='utf-8',errors='xmlcharrefreplace') as f:
    namesInfo = json.loads(f.read())
importantNames = namesInfo['names'] # Alle 6468 auftretenden Spaltennamen

i = -1
for colName in columnNames:
    print('\nCheck column "'+colName+'":')
    i += 1
    if i == 0:
        print('Abort checking (is key column)')
        continue

    if len(colName) <= 1:
        colOnts.append({colName: None})
        print('Column name "'+colName+'" is too short (Length: '+len(colName)+')')
        continue

    prepColName = colName.replace('\n',' ')
    regPattern = re.compile('\[[0-9]*\]')
    prepColName = regPattern.sub('', prepColName)
    prepColName = prepColName.strip()

    suggestedName = process.extractOne(prepColName, list(importantNames.keys()))
    print(importantNames[suggestedName[0]])
"""
