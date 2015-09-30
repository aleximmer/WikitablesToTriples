# -*- coding: utf-8 -*-
import inflect
import math
import sys
import re
import json
import traceback
import copy

from bs4 import BeautifulSoup
from more_itertools import unique_everseen
from fuzzywuzzy import fuzz

# Thresholds:

# KeyCol needs to be unique
ONLY_UNIQUE_COLS = False
# At least {x*100} percent have to be entities, so that the column may be a key
MIN_ENTITIES_COUNT = 0.4
# For having 100% entities, the column receives {x} rating points
MAX_ENTITIES_POINTS = 50
# Columns with the name "Name", "Title" or "Type" receive {x} rating points
COLNAME_NAME_POINTS = 20
# Each word can bring not more than {x} rating points
COLNAME_MAX_WORD_POINTS = 20
# Hits for generated plural forms yield {x} rating points
COLNAME_PLURAL_HIT_POINTS = 10
# Each match for a word in the Abstract generates {x} rating points
COLNAME_ABSTRACTS_SCALE = 4
# The left column receives {x} rating points. The points distribution decreases
# hyperbolically to the right
COLPOS_MAX_POINTS = 20
# A column using <th>-Tags for its entries receives {x} rating points
COL_TH_POINTS = 20
# The FuzzyWuzzy rating value for list categories has to be over the value {x}
LISTCAT_RATIO = 90
# An hit for a list category yields {x} rating points
LISTCAT_MATCH_POINTS = 4
# The column with the second highest rating score must be lower than the highest
# score multiplied with {x}
FIRST_SECOND_RATIO = 0.95

# Initialize Inflect Engine
inflectEngine = inflect.engine()

########################################## Key extraction ################

# Ermittelt mittels dem BeautifulSoup-Package die Kopfzeile der Tabelle und
# gibt alle Header als Array von Soup-Elemente zurück.
# Sollte die Kopfzeile nicht gefunden werden oder kein Header vorhanden,
# wirft die Funktion einen ValueError.


class KeyExtractor:
    # TODO: Docstring

    def __init__(self, table):
        self.originalHTMLSoup = table.soup
        self.articleName = table.page.title
        self.abstracts = table.page.summary
        self.listCategories = table.page.categories

    def _extractTableHead(self, htmlTableSoup):
        htmlTable = str(htmlTableSoup)
        quickView = htmlTable[0:50] + " [...]"

        # Erste Row (TR) egal ob im TBody oder sogar im THead ist die Kopfzeile
        # (Aussage mit Tests überprüfen?)
        header = htmlTableSoup.find("tr")
        if header == None:
            raise ValueError(
                "Can\'t find header row of the given table: \n" + quickView)

        colNames = header.findAll("th")
        if (len(colNames) == 0):
            raise ValueError(
                "Can\'t find header row of the given table: \n" + quickView)

        return [entry.getText() for entry in colNames]

    # <th> tags are used in different ways so it's nearly impossible to parse them
    # Solution: replace them with <td> and act like the <td>-Tags in the first
    # <tr>-Row are <th>-Tags
    def _fixTableHeaderTagsForOutput(self, htmlTableSoup):
        thTags = htmlTableSoup.findAll('th')

        for thTag in thTags:
            thTag.name = 'td'

        htmlTable = str(htmlTableSoup)

        # Make the first row to a header row (<td> to <th>)
        pos1 = htmlTable.find("<tr")
        pos2 = htmlTable.find("</tr>") + 5
        firstRow = htmlTable[pos1:pos2]

        headerSoup = BeautifulSoup(firstRow, "lxml")
        colNames = headerSoup.findAll('td')
        for col in colNames:
            col.name = 'th'
        # FirstRow without <html><body></body></html>
        firstRow = str(headerSoup.body.next)

        return BeautifulSoup(htmlTable[:pos1] + firstRow + htmlTable[pos2:], "lxml")

    # Ermittelt alle Spalten der Tabelle (ohne die Header-Felder) und überprüft
    # diese auf Einzigartigkeit (optional). Sollte keine Spalte dem entsprechen, wird˚
    # ein ValueError geworfen.˚
    # Am Ende wird ein Array von Elementen der Form {"xPos": a, "entries": c}
    # zurückgegeben
    # UPDATE: Added originalHTML and attrOrig to get the real tag (th or td)
    # htmlTableSoup = th and td tags by _fixTableHeaderTagsForOutput() formatted
    def _extractColumnsInfos(self, htmlTableSoup):
        quickView = str(self.originalHTMLSoup)[0:50] + " [...]"  # error output

        # 1.) Überprüfen ob die Tabelle ein gültiges Format hat
        it = re.finditer('(rowspan|colspan)="([0-9]*)"', str(self.originalHTMLSoup))
        for match in it:
            spanVal = match.group(2)
            if spanVal != "1":
                raise ValueError("Table uses not supported formattings (" + match.group(
                    1) + " at " + str(match.span()) + "): " + match.group())

        # 2.) Alle Spalten als 2D-Array extrahieren
        rows = htmlTableSoup.findAll("tr")
        rowsOrig = self.originalHTMLSoup.findAll("tr")
        rowCount = len(rows) - 1
        if rowCount <= 0:
            raise ValueError("Table doesn\'t contain rows (except the head line): " + quickView)
        colCount = len(rows[1].findAll("td"))
        if colCount <= 0:
            raise ValueError("Table doesn\'t contain columns in row 1: " + quickView)

        # 3.) 2D-Array der HTML-Tabelle reihenweise erzeugen
        tableData = [[dataField.getText() for dataField in rows[i].findAll("td")] for i in range(1, rowCount + 1)]
        tableDataRaw = [[str(dataField) for dataField in rows[i].findAll("td")] for i in range(1, rowCount + 1)]
        tableDataRawOrig = [[str(dataField) for dataField in rowsOrig[i].findAll(["th", "td"])] for i in range(1, rowCount + 1)]

        # 4.) Zu jeder Spalte überprüfen, ob die Einträge einzigartig sind
        # Es wird der Plain-Text verglichen, aber der ganze HTML-Code
        # gespeichert
        uniqueCols = []
        for j in range(colCount):
            # Bereits angesehen Werte zwischenspeichern (für
            # Einzigartigkeits-Check)
            checkedValues = [0 for i in range(rowCount)]
            unique = True
            for i in range(rowCount):
                # FIXME: Error "tableData[i][j] list index out of range" -> tableData[0] leer -> findAll("td") hat nichts gefunden
                # -> Header-Zeile wurde mitgelesen (soll nicht passieren)

                # Take plain text and remove alle white spaces from the side
                value = tableData[i][j].strip()
                if len(value) > 0:
                    if value in checkedValues:
                        # FIXME: Manche Zwischen-Header-Zeilen mit leeren Zellen haben ein unsichtbares
                        # y mit Ü-Pünktchen (e.g. List of airports in France >
                        # Airports in Metropolitan France)
                        unique = False
                        break
                    else:
                        checkedValues[i] = value
            if unique or not ONLY_UNIQUE_COLS:
                # Alle Einträge der möglichen Key-Spalte als Array speichern
                # (plain, nicht raw)
                uniqueCols.append({"xPos": j,
                                   "unique": unique,
                                   "entries": [tableDataRaw[x][j] for x in range(rowCount)],
                                   "entriesOrig": [tableDataRawOrig[x][j] for x in range(rowCount)]})
                # print(str(j), str(unique), tableDataRawOrig[0][j], str([0]))
        if len(uniqueCols) == 0:
            raise ValueError(
                "Can\'t find any column with unique entries (might be foreing keys)")

        # Führe Title mit Entries und Position zusammen (Schema):
        tableColNames = self._extractTableHead(htmlTableSoup)
        uniqueCols = [{
            "xPos": col["xPos"],
            "unique": col["unique"],
            "title": tableColNames[col["xPos"]],
            "entries": col["entries"],
            "entriesOrig": col["entriesOrig"],
            "rating": 0}
            for col in uniqueCols]

        return uniqueCols

    # Zählt ab, wie viele Einträge pro Spalte Links enthalten. Die Links werden
    # als Entitäten gewertet, wenn sie kein Image enthalten und
    # Wikipedia-intern sind (Präfix: "/wiki/...")
    # Prozentual betrachtet wird jeder Spalte eine Bewertung gegeben. Wenn 100%
    # der Einträge einer Spalte Entitäten sind, werden 50 Punkte vergeben.
    def _countEntities(self, cols):
        for i in range(len(cols)):
            entries = cols[i]["entries"]
            entityCount = 0
            multipleEnts = False
            for entry in entries:
                entrySoup = BeautifulSoup(entry, "lxml")
                links = entrySoup.findAll("a")
                linksHref = [aTag["href"] for aTag in links]
                linksHref = list(unique_everseen(linksHref))
                linksCount = len(links)
                for link in links:
                    # Image werden nicht gezählt
                    if link.find("img"):
                        linksCount -= 1
                    # Ebenso dürfen es nur Wikipedia-interne Links sein
                    elif 'wiki' not in link["href"]:
                        linksCount -= 1
                    # Manche Tabellen setzen doppelte Verlinkunden (e.g.
                    # TableID = 513, List of Olympic medalists in basketball)
                    elif link["href"] in linksHref:
                        # Beim ersten Mal löschen
                        linksHref.remove(link["href"])
                    elif link["href"] not in linksHref:
                        linksCount -= 1  # Bei jedem weiteren Mal, die Anzahl korrigieren
                if linksCount > 0:
                    entityCount += 1
                    if linksCount > 1:
                        multipleEnts = True

            # Bewertung: Maximal 50 Punkte möglich (100% sind Entitäten)
            cols[i]["rating"] = int(math.floor(
                MAX_ENTITIES_POINTS * (entityCount / len(entries))))
            cols[i]["entityCount"] = entityCount
            cols[i]["multipleEntities"] = multipleEnts

    # Überprüft, ob im Spaltentitel das Wort "Name", "Title" oder "Type" auftaucht (+20 Rating)
    # oder Übereinstimmungen mit dem Titel des Wikipedia-Artikels existieren.
    # Dabei wird der Singular und Plural betrachtet. Umso länger ein Wort ist,
    # für das eine Übereinstimmung gefunden wurde, desto mehr Punkte gibt es
    # im Rating (maximal 20/25), damit Nebenwörter wie "in", "the", "of", o.ä.
    # wenig Einfluss haben.
    def _valuateByName(self, cols):
        # Entferne "List of" und teile die Wörter auf
        articleNames = self.articleName[7:].split(" ")

        for i in range(len(cols)):
            colName = cols[i]["title"]
            colNames = colName.lower().split()
            # Titel auf den Inhalt "Name", "Title" und "Type" überprüfen
            if "name" in colNames or "title" in colNames or "type" in colNames:
                cols[i]["rating"] += COLNAME_NAME_POINTS

            # Titel mit dem Artikelnamen abgleichen
            for word in colNames:
                if word in articleNames:
                    # Wenn eines der Wörter auch im Artikelnamen auftaucht, erhöht das das Rating
                    # Die gegebene Punktzahl ist von der Wortlänge abhängig (Problematische Wörter
                    # wie "in", "the", "of" o.ä. haben dann wenig Einfluss)
                    cols[i]["rating"] += max(len(word),
                                             COLNAME_MAX_WORD_POINTS)
                if inflectEngine.plural(word) in articleNames:
                    # Wenn der Plural trifft, ist es ein wichtigerer Treffer
                    # als ein normaler
                    cols[i][
                        "rating"] += max(len(word), COLNAME_MAX_WORD_POINTS) + COLNAME_PLURAL_HIT_POINTS

    # Umso näher die Spalte am linken Rand ist, desto wichtiger ist sie.
    # Es können maximal 20 Punkte aufgerechnet werden (für die erste Spalte).
    # Nach rechts hin nimmt die Punktvergabe hyperbolisch ab.
    def _valuateByPosition(self, cols):
        colLen = len(cols)
        for i in range(colLen):
            posVal = i + 1
            # Quadratische Verteilung: 20, 16, 12, 9, 7, 5, ...
            # Hyperbolische Verteilung: 20, 10, 6, 5, 4, ...
            # Hyperbolisch
            addRating = int(math.floor(COLPOS_MAX_POINTS / posVal))
            cols[i]["rating"] += addRating

    # Manche Tabellen benutztn <th>-Tags vertikal. Diese Spalten haben mit
    # hoher Warscheinlichkeit die gesuchten Entitäten (KeyCol)
    def _lookForTHCol(self, uniqueCols):
        for col in uniqueCols:
            isVertical = True
            for entry in col['entriesOrig']:
                if entry[:3] != '<th':
                    isVertical = False
                    break
            if isVertical:
                col['rating'] += COL_TH_POINTS

    # Find matches for each column name with the table abstracts.
    # Add for each match of a word (or its plural form) in the column name
    # rating points to the column.
    def _textualEvidenceWithAbstracts(self, uniqueCols, abstracts):
        if len(abstracts) > 0:
            for col in uniqueCols:
                colName = col['title']
                for colWord in colName.split(' '):
                    if len(colWord) > 2:
                        colWordPl = re.escape(inflectEngine.plural(colWord))
                        colWord = re.escape(colWord)
                        occCount = len(re.findall(
                            '(' + colWord + '|' + colWordPl + ')', abstracts, flags=re.IGNORECASE))
                        # Rating by occurrence
                        col['rating'] += occCount * COLNAME_ABSTRACTS_SCALE
    # Find matches between column names and categories of the regarding list page.
    # Add for each match of a word (or its plural form) in the column name
    # rating points to the column.

    def _findMatchWithListCategories(self, uniqueCols, listCategories):
        for col in uniqueCols:
            for cat in listCategories:
                cat = cat.lower()
                for colWord in col['title'].split(' '):
                    if len(colWord) > 2:
                        rating = fuzz.partial_ratio(colWord, cat)
                        if rating > LISTCAT_RATIO:
                            col['rating'] += LISTCAT_MATCH_POINTS

    # Vergleicht die Ratings der Spalten, um die Key-Spalte zu ermitteln.
    # Das größte Rating muss 15% vor dem zweiten liegen. Außerdem müssen
    # mind. 40% der Einträge Entitäten sein. Wenn keine Key-Spalte gefunden
    # wurde, wird None zurückgegeben (ansonsten das Spaltenelement)
    def _validateRatings(self, cols):
        # Create copy to keep the original order in cols
        ratCols = [{'entries': col['entries'],
                    #'entriesOrig': col['entriesOrig'],
                    'unique': col['unique'],
                    'rating': col['rating'],
                    'entityCount': col['entityCount'],
                    'multipleEntities': col['multipleEntities'],
                    'xPos': col['xPos'],
                    'title': col['title']} for col in cols]
        ratCols.sort(key=lambda obj: obj['rating'], reverse=True)
        rating1 = ratCols[0]['rating']
        #print(len(ratCols))
        #print(ratCols[len(ratCols)-1]['rating'], ratCols[len(ratCols)-1]['title'], ratCols[len(ratCols)-1]['entries'][0])
        if len(ratCols) > 1:
            rating2 = ratCols[1]['rating']
            # Wenn der erste und zweite Platz zu nah sind, ist das Ergebnis
            # nicht eindeutig genug
            if (rating2 / rating1) > FIRST_SECOND_RATIO:
                print('no prominent candidate for key')
                return None

        # Die Entitäten müssen eindeutig sein (Max. eine Entität pro Feld)
        if ratCols[0]["multipleEntities"]:
            print("elements in candidate column not unique")
            return None

        rowCount = len(ratCols[0]["entries"])
        entityCount = ratCols[0]["entityCount"]
        # Wenn weniger als 40% der Einträge Entitäten sind, ist die Spalte
        # nicht ausreichend verwertbar
        if (entityCount / rowCount) < MIN_ENTITIES_COUNT:
            print("too few resources in candidate column")
            return None

        return ratCols[0]

    def extractKeyColumn(self):
        # Fix <th> tags because <th> is used in different ways:
        # Save original formatting as copy (force copying)
        htmlTableSoup = BeautifulSoup(str(self.originalHTMLSoup), "lxml")
        htmlTableSoup = self._fixTableHeaderTagsForOutput(htmlTableSoup)

        # Extracting and rating columns
        uniqueCols = self._extractColumnsInfos(htmlTableSoup)

        # Rating:

        # Zähle die Entities pro Spalte
        self._countEntities(uniqueCols)

        # Kommt der Artikelname oder das Wort 'Name' im Spaltenname vor
        self._valuateByName(uniqueCols)

        # Umso weiter links, umso wertvoller ist die Spalte
        self._valuateByPosition(uniqueCols)

        # Nutze vertikale TH-Cols
        self._lookForTHCol(uniqueCols)

        # Spaltenname mit der Beschreibung (Abstracts) der Tabelle abgleichen (ähnlich wie mit dem Artikel-Name)
        #_textualEvidenceWithAbstracts(uniqueCols, abstracts)

        # Listen-Kategorien mit den Spaltennamen abgleichen
        #_findMatchWithListCategories(uniqueCols, listCategories)

        # Validiere die Bewertungen der Spalten
        keyCol = self._validateRatings(uniqueCols)

        return keyCol['xPos'] if keyCol else -1


class KeyExtractionError(Exception):
    pass
