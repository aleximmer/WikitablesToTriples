# -*- coding: utf-8 -*-
import codecs
import json
import extensions.inflect as inflect
import math
import sys
import re
import traceback

from bs4 import BeautifulSoup
from  more_itertools import unique_everseen

# Nach TR-Tag suchen (muss THs enthalten)
# 1.) Von dort die THs extrahieren als Header-Array und als JSON ausgeben
# 2.) Spalten in 2D-Array abspeichern und auf Einzigartigkeit überprüfen

# Soup-Element ausgeben:
# Mit Tags (inkl. Links der Entitäten) -> str(obj)
# Nur Plain Text: obj.getText()

# Engine, um Singular und Plural von Wörtern zu bilden
p = inflect.engine()

# Thresholds:
ONLY_UNIQUE_COLS = False # KeyCol muss einzigartig sein
MIN_ENTITIES_COUNT = 0.4 # Mind. {x} in Prozent müssen Entities sein, damit die Spalte der Key sein darf
MAX_ENTITIES_POINTS = 50 # Bei 100% Entitäten gibt es {x} Punkte
COLNAME_NAME_POINTS = 20 # Wenn der Spaltenname "Name" oder "Title" enthält, gibt's {x} Punkte
COLNAME_MAX_WORD_POINTS = 20 # Wenn ein Wort-Treffer kann max {x} Punkte einbringen
COLNAME_PLURAL_HIT_POINTS = 10 # Wenn ein Wort-Treffer über den Plural trifft, gibt es {x} Punkte zusätzlich
COLPOS_MAX_POINTS = 20 # Die linke Spalte bekommt {x} Punkte und ab da nach rechts hyperbolisch abwärts
COL_TH_POINTS = 20 # Eine Spalte mit <th>-Tags erhält {x} Punkt
FIRST_SECOND_RATIO = 0.95 # Die zweit-höchste Spalte darf höchstens {x} (in Prozent) von der besten Spalte sein

# DEPRECATED
# Konstantendefinition für Rückgabewert-Typen
def RETURN_AS_SOUP_ARRAY(): return 0
def RETURN_AS_STRING_ARRAY(): return 1
def RETURN_AS_JSON_STRING(): return 2
def returnWithType( obj, returnType):
	if returnType == RETURN_AS_SOUP_ARRAY():
		return obj
	elif returnType == RETURN_AS_STRING_ARRAY():
		return [entry.getText() for entry in obj]
	elif returnType == RETURN_AS_JSON_STRING():
		return json.dumps(obj, default=lambda entry: entry.getText(), sort_keys=True, indent=4)
	else:
		raise ValueError("Illegal value for returnType: \'" + returnType + "lat (Allowed: 0, 1 or 2) ")

# Ermittelt mittels dem BeautifulSoup-Package die Kopfzeile der Tabelle und
# gibt alle Header als Array von Soup-Elemente zurück.
# Das Rückgabe-Format kann mit oben gegebenen Konstanten geändert werden.
# Sollte die Kopfzeile nicht gefunden werden oder kein Header vorhanden,
# wirft die Funktion einen ValueError.
def extractTableHead( htmlTable, returnType = RETURN_AS_SOUP_ARRAY() ):
	soup = BeautifulSoup(htmlTable)
	quickView = htmlTable[0:50]+" [...]"
	
	# Erste Row (TR) egal ob im TBody oder sogar im THead ist die Kopfzeile (Aussage mit Tests überprüfen?)
	header = soup.find("tr")
	if header == None:
		raise ValueError("Can\'t find header row of the given table: \n" + quickView)
	
	colNames = header.findAll("th")
	if (len(colNames) == 0):
		raise ValueError("Can\'t find header row of the given table: \n" + quickView)
	
	return returnWithType( colNames, returnType)
	

########################################## Key extraction ##########################################

# <th> tags are used in different ways so it's nearly impossible to parse them
# Solution: replace them with <td> and act like the <td>-Tags in the first <tr>-Row are <th>-Tags
def fixTableHeaderTagsForOutput( htmlTable ):
	soup = BeautifulSoup(htmlTable)
	thTags = soup.findAll('th')
	
	for thTag in thTags:
		thTag.name='td'
	htmlTable = str(soup)
	
	# TODO: Erkennen ob die erste Zeile wirklich der Header ist oder es keinen gibt
	# Make the first row to a header row (<td> to <th>)
	pos1 = htmlTable.find("<tr")
	pos2 = htmlTable.find("</tr>") + 5
	firstRow = htmlTable[pos1:pos2]
	
	soup = BeautifulSoup(firstRow)
	colNames = soup.findAll('td')
	for col in colNames:
		col.name='th'
	firstRow = str(soup.body.next)
	return htmlTable[:pos1] + firstRow + htmlTable[pos2:]
	

# Benutze BeautifulSoup, um alle Spalten abzuzählen. In der ersten Reihe dürfen td & th stehen
def countAllCols( htmlTable ):
	soup = BeautifulSoup(htmlTable)
	firstRow = soup.find("tr")
	return len(firstRow.findAll("th") + firstRow.findAll("td"))

# Ermittelt alle Spalten der Tabelle (ohne die Header-Felder) und überprüft
# diese auf Einzigartigkeit(optional). Sollte keine Spalte dem entsprechen, wird
# ein ValueError geworfen.
# Am Ende wird ein Array von Elementen der Form {"xPos": a, "entries": c}
# zurückgegeben
# UPDATE: Added originalHTML and attrOrig logic to save the real tag (hd or td)
def extractColumnsInfos( htmlTable, originalHTML ):
	soup = BeautifulSoup(htmlTable)
	soupOrig = BeautifulSoup(originalHTML)
	quickView = originalHTML[0:50]+" [...]"
	
	# 1.) Überprüfen ob die Tabelle ein gültiges Format hat
	it = re.finditer('(rowspan|colspan)="([0-9]*)"', htmlTable)
	for match in it:
		spanVal = match.group(2)
		if spanVal != "1":
			raise ValueError("Table uses not supported formattings ("+match.group(1)+" at "+str(match.span())+"): " + match.group())
	
	# 2.) Alle Spalten als 2D-Array extrahieren
	rows = soup.findAll("tr")
	rowsOrig = soupOrig.findAll("tr")
	rowCount = len(rows)
	colCount = len(rows[0].findAll("td"))
	firstLineIsHeader = False
	# Wenn die erste Zeile die Kopfzeile war, hat sie keine td-Tags -> Nächste Zeile nehmen
	if colCount == 0:
		if rowCount > 1:
			firstLineIsHeader = True
			colCount = len(rows[1].findAll("td"))
			rowCount -= 1
		else:
			raise ValueError("Table doesn\'t contain rows (except the head line): " + quickView)
	
	# 3.) 2D-Array der HTML-Tabelle reihenweise erzeugen
	# Es wird nur der richtige Plaintext verglichen, aber der ganze HTML-Code gespeichert
	if firstLineIsHeader:
		tableData = [[dataField.getText() for dataField in rows[i+1].findAll("td")] for i in range(rowCount)]
		tableDataRaw = [[str(dataField) for dataField in rows[i+1].findAll("td")] for i in range(rowCount)]
		tableDataRawOrig = [[str(dataField) for dataField in rowsOrig[i+1].findAll(["th", "td"])] for i in range(rowCount)]
	else:
		tableData = [[dataField.getText() for dataField in rows[i].findAll("td")] for i in range(rowCount)]
		tableDataRaw = [[str(dataField) for dataField in rows[i].findAll("td")] for i in range(rowCount)]
		tableDataRawOrig = [[str(dataField) for dataField in rowsOrig[i].findAll(["td", "th"])] for i in range(rowCount)]
	
	# 4.) Zu jeder Spalte überprüfen, ob die Einträge einzigartig sind (Vergleicht dafür inkl. Tags)
	uniqueCols = []
	for j in range(colCount):
		# Bereits angesehen Werte zwischenspeichern (für Einzigartigkeits-Check)
		checkedValues = [0 for i in range(rowCount)]
		unique = True
		for i in range(rowCount):
			#FIXME: "list index out of range" -> tableData[0] leer -> findAll("td") hat nichts gefunden
			# -> Header-Zeile wurde mitgelesen (soll nicht passieren)
			
			# Take plain text and remove alle white spaces from the side
			value = tableData[i][j].strip()
			if len(value) > 0:
				if value in checkedValues:
					#FIXME: Manche Zwischen-Header-Zeilen mit leeren Zellen haben ein unsichtbares 
					# y mit Ü-Pünktchen (e.g. List of airports in France > Airports in Metropolitan France)
					unique = False
					break
				else:
					checkedValues[i] = value
		if unique or not ONLY_UNIQUE_COLS:
			# Alle Einträge der möglichen Key-Spalte als Array speichern (plain, nicht raw)
			uniqueCols.append({"xPos": j,
				"unique": unique,
				"entries": [tableDataRaw[x][j] for x in range(rowCount)],
				"entriesOrig": [tableDataRawOrig[x][j] for x in range(rowCount)]})
	if len(uniqueCols) == 0:
		raise ValueError("Can\'t find any column with unique entries (might be foreing keys)")

	# Führe Title mit Entries und Position zusammen (Schema):
	tableColNames = extractTableHead(htmlTable, RETURN_AS_STRING_ARRAY())
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
# TODO: Weitere Einschränkungen möglich? (Umso mehr Text vor dem Link o.ä.)
def countEntities( cols ):
	for i in range(len(cols)):
		entries = cols[i]["entries"]
		entityCount = 0
		multipleEnts = False
		for entry in entries:
			soup = BeautifulSoup(entry)
			links = soup.findAll("a")
			linksHref = [aTag["href"] for aTag in links]
			linksHref = list(unique_everseen(linksHref))
			linksCount = len(links)
			for link in links:
				# Image werden nicht gezählt
				if link.find("img") != None:
					linksCount -= 1
				# Ebenso dürfen es nur Wikipedia-interne Links sein
				elif link["href"][0:5] != "/wiki":
					linksCount -= 1
				# Manche Tabellen setzen doppelte Verlinkunden (e.g. TableID = 513, List of Olympic medalists in basketball)
				elif link["href"] in linksHref:
					linksHref.remove(link["href"]) # Beim ersten Mal löschen
				elif link["href"] not in linksHref:
					linksCount -= 1 # Bei jedem weiteren Mal, die Anzahl korrigieren
			if linksCount > 0:
				entityCount += 1
				if linksCount > 1:
					multipleEnts = True
		
		# Bewertung: Maximal 50 Punkte möglich (100% sind Entitäten)
		cols[i]["rating"] = int(math.floor(MAX_ENTITIES_POINTS * (entityCount / len(entries))))
		cols[i]["entityCount"] = entityCount
		cols[i]["multipleEntities"] = multipleEnts

# Überprüft, ob im Spaltentitel das Wort "Name" auftaucht (+20 Rating)
# oder Übereinstimmungen mit dem Titel des Wikipedia-Artikels existieren.
# Dabei wird der Singular und Plural betrachtet. Umso länger ein Wort ist,
# für das eine Übereinstimmung gefunden wurde, desto mehr Punkte gibt es
# im Rating (maximal 20/25), damit Nebenwörter wie "in", "the", "of", o.ä.
# wenig Einfluss haben.
def valuateByName( cols, articleName ):
	# Entferne "List of" und teile die Wörter auf
	articleNames = articleName[7:].split(" ")
	
	for i in range(len(cols)):
		colName = cols[i]["title"]
		colNames = colName.lower().split()
		# Titel auf den Inhalt "Name" oder "Title" überprüfen
		if "name" in colNames or "title" in colNames:
			cols[i]["rating"] += COLNAME_NAME_POINTS
		
		# Titel mit dem Artikelnamen abgleichen
		for word in colNames:
			if word in articleNames:
				# Wenn eines der Wörter auch im Artikelnamen auftaucht, erhöht das das Rating
				# Die gegebene Punktzahl ist von der Wortlänge abhängig (Problematische Wörter
				# wie "in", "the", "of" o.ä. haben dann wenig Einfluss)
				cols[i]["rating"] += max(len(word), COLNAME_MAX_WORD_POINTS)
			if p.plural(word) in articleNames:
				# Wenn der Plural trifft, ist es ein wichtigerer Treffer als ein normaler
				cols[i]["rating"] += max(len(word), COLNAME_MAX_WORD_POINTS) + COLNAME_PLURAL_HIT_POINTS

# Umso näher die Spalte am linken Rand ist, desto wichtiger ist sie.
# Es können maximal 20 Punkte aufgerechnet werden (für die erste Spalte).
# Nach rechts hin nimmt die Punktvergabe hyperbolisch ab.
# TODO: Linear, Quadratisch oder Hyperbolisch?
def valuateByPosition( cols ):
	colLen = len(cols)
	for i in range(colLen):
		posVal = i + 1
		# Quadratisch bei 10 Spalten: 20, 16, 12, 9, 7, 5, ...
		# Hyperbel bei 10 Spalten: 20, 10, 6, 5, 4, ...
		addRating = int(math.floor(COLPOS_MAX_POINTS / posVal)) # Hyperbolisch
		cols[i]["rating"] += addRating

# Manche Tabellen benutztn <th>-Tags vertikal. Diese Spalten sind mit
# hoher Warscheinlichkeit die gesuchten Entitäten (KeyCol)
def lookForTHCol( uniqueCols, originalHTML ):
	for i in range(0, len(uniqueCols)):
		isVertical = True
		for entry in uniqueCols[i]['entriesOrig']:
			if entry[:3] != '<th':
				isVertical = False
				break;
		if isVertical:
			uniqueCols[i]['rating'] += COL_TH_POINTS

def textualEvidenceWithAbstracts( uniqueCols, abstracts ):
	abstractsWords = abstracts.split(" ")
	print('TODO: Get abstracts of table (Wörter: '+str(abstractsWords)+')')
	# TODO: Abstracts in DB speichern
	# TODO: in valuateByName übernehmen

def findFittingColumnProperties( uniqueCols ):
	print('TODO: Get sparql connection')
	# TODO: Properties über SparQL holen
	# TODO: Property-Name mit Colum-Namen abgleichen

def findMatchWithListCategories( uniqueCols, articleName):
	print('TODO: Get sparql connection')
	# TODO: Kategorien einer Liste(articleName) per SparQL holen
	# TODO: Kategorien-Name über Textual-Evidence mit dem Spaltennamen abgleichen

# Vergleicht die Ratings der Spalten, um die Key-Spalte zu ermitteln.
# Das größte Rating muss 15% vor dem zweiten liegen. Außerdem müssen
# mind. 40% der Einträge Entitäten sein. Wenn keine Key-Spalte gefunden
# wurde, wird None zurückgegeben (ansonsten das Spaltenelement)
def validateRatings( cols ):
	# TODO: Ausgangsposition speichern oder nur max und 2-max herausfinden
	# Create copy to keep the original order in cols
	ratCols = [{'entries': col['entries'], 'rating': col['rating'], 'entityCount': col['entityCount'], 'multipleEntities': col['multipleEntities'], 'xPos': col['xPos']} for col in cols]
	ratCols.sort(key=lambda obj: obj['rating'], reverse=True)
	rating1 = ratCols[0]['rating']
	if len(ratCols) > 1:
		rating2 = ratCols[1]['rating']
		# Wenn der erste und zweite Platz zu nah sind, ist das Ergebnis nicht eindeutig genug
		if (rating2 / rating1) > FIRST_SECOND_RATIO:
			print("Algorithm failed: Not clear enough")
			return None
	
	# Die Entitäten müssen eindeutig sein (Max. eine Entität pro Feld)
	if ratCols[0]["multipleEntities"]:
		print("Algorithm failed: Entries contain more than one entity")
		return None
	
	rowCount = len(ratCols[0]["entries"])
	entityCount = ratCols[0]["entityCount"]
	# Wenn weniger als 40% der Einträge Entitäten sind, ist die Spalte nicht ausreichend verwertbar
	if (entityCount / rowCount) < MIN_ENTITIES_COUNT:
		print("Algorithm failed: Too less entities")
		return None
	
	return ratCols[0]

# Um die Testergebnisse zu visualisieren, werden die Ergebnisse
# der drei Runden als CSV gespeichert
def saveCSVData( roundsResults, cols, round ):
	roundsResults.append([])
	for col in cols:
		roundsResults[round].append(col["rating"])

# TODO: Dokumentieren
def extractKeyColumn( htmlTable, articleName, tableName, abstracts ):
	try:
		"""
		try:
		    print(htmlTable[0:500])
		    print(articleName)
		except Exception as e:
		    print(articleName)
		    raise ValueError('Table contains not supported characters - Error message: \n' + str(e))
		"""

		# Fix <th> tags because <th> is used in different ways:
		originalHTML = (htmlTable + '.')[:-1] # Save original formatting as copy (force copying)
		htmlTable = fixTableHeaderTagsForOutput(htmlTable)

		# Extracting and rating columns
		uniqueCols = extractColumnsInfos(htmlTable, originalHTML)

		# Rating:

		# Zähle die Entities pro Spalte
		countEntities(uniqueCols)

		# Kommt der Artikelname oder das Wort 'Name' im Spaltenname vor
		valuateByName(uniqueCols, articleName)

		# Umso weiter links, umso wertvoller ist die Spalte
		valuateByPosition(uniqueCols)

		# Nutze vertikale TH-Cols
		lookForTHCol(uniqueCols, originalHTML)

		# Spaltenname mit der Beschreibung (Abstracts) der Tabelle abgleichen (ähnlich wie mit dem Artikel-Name)
		# TODO: textualEvidenceWithAbstracts(uniqueCols, abstracts)

		# Properties der Spalteneinträge mit den anderen Spaltennamen abgleichen
		# TODO: findFittingColumnProperties(uniqueCols)

		# Listen-Kategorien mit den Spaltennamen abgleichen
		# TODO: findMatchWithListCategories(uniqueCols, articleName)

		# Validiere die Bewertungen der Spalten
		keyCol = validateRatings(uniqueCols)

		# Für das Frontend wird die gesamte Anzahl an Spalten benötigt
		colCount = countAllCols(htmlTable)

		if keyCol != None:
		    keyCol = keyCol['xPos']
		else:
		    print('Can\'t extract a significant single key column')
		    keyCol = -1

	except Exception as e:
		# Might be an error caused by wrong html format or unsupported html encoding
		# raise e
		print('Error: ' + str(e))
		print(traceback.format_exc())
		keyCol = -1
		uniqueCols = []
		colCount = countAllCols(htmlTable)
	
	return {'originalHTML': originalHTML, 'uniqueCols': uniqueCols, 'colCount': colCount, 'keyCol': keyCol}


# TODO: Dokumentieren
def calculatePrecisionRecall( tables, debug=False ):
	# True positives -> Right key selected
	countTP = 0
	# True negative -> Detected that there is no valid key column
	countTN = 0
	# False positive -> Detects mistakenly a key column or the wrong key column
	countFP = 0
	countWC = 0
	# False negative -> Can't find an existing key column
	countFN = 0
	
	for table in tables:
		algoCol = str(table.algo_col)
		humCol = (table.hum_col)
		print(str(table.id) +': ' + algoCol + ' but is ' + humCol)
		
		# There is no key column
		if humCol == '-1':
			if algoCol == '-1': # Algorithm is right ("no detectable key column")
				countTN += 1
			else: # Algorithm is wrong (suggests a key column although there is no column)
				countFP += 1
		# There is a key column at position {x}
		else:
			if algoCol == humCol: # Algorithm is right ("found key column")
				countTP += 1
			elif algoCol == '-1': # Algorithm is wrong (didn't find the existing key column)
				countFN += 1
			else: # Algorithm is wrong (suggests the wrong column as key column)
				countWC += 1
	if debug:
		asString =  'True positive: '+str(countTP)+'\n'
		asString += 'True negative: '+str(countTN)+'\n'
		asString += 'False positive: '+str(countFP+countWC)+' ('+str(countWC)+' wrong columns + '+str(countFP)+' non existing columns) \n'
		asString += 'False negative: '+str(countFN)+'\n'
		print(asString)
	
	countFP += countWC
	if (countTP+countFP) > 0 and (countTP+countFN) > 0:
		precision = round(countTP / (countTP + countFP), 2)
		recall = round(countTP / (countTP + countFN), 2)
	else:
		precision = 0
		recall = 0
	thresholdsState = {
		'ONLY_UNIQUE_COLS': ONLY_UNIQUE_COLS, # KeyCol muss einzigartig sein
		'MIN_ENTITIES_COUNT': MIN_ENTITIES_COUNT, # Mind. {x} in Prozent müssen Entities sein, damit die Spalte der Key sein darf
		'MAX_ENTITIES_POINTS': MAX_ENTITIES_POINTS, # Bei 100% Entitäten gibt es {x} Punkte
		'COLNAME_NAME_POINTS': COLNAME_NAME_POINTS, # Wenn der Spaltenname "Name" oder "Title" enthält, gibt's {x} Punkte
		'COLNAME_MAX_WORD_POINTS': COLNAME_MAX_WORD_POINTS, # Wenn ein Wort-Treffer kann max {x} Punkte einbringen
		'COLNAME_PLURAL_HIT_POINTS': COLNAME_PLURAL_HIT_POINTS, # Wenn ein Wort-Treffer über den Plural trifft, gibt es {x} Punkte zusätzlich
		'COLPOS_MAX_POINTS': COLPOS_MAX_POINTS, # Die linke Spalte bekommt {x} Punkte und ab da nach rechts hyperbolisch abwärts
		'COL_TH_POINTS': COL_TH_POINTS, # Eine Spalte mit <th>-Tags erhält {x} Punkt}
		'FIRST_SECOND_RATIO': FIRST_SECOND_RATIO} # Die zweit-höchste Spalte darf höchstens {x} (in Prozent) von der besten Spalte sein
	
	if debug:
		asString = 'Precision: '+str(precision*100)+'%\nRecall: '+str(recall*100)+'%\n'
		print(asString)
	return {'precision': precision, 'recall': recall, 'tableCount': len(tables), 'thresholdsState':thresholdsState}

def machineLearningWithPrecisionRecall( tables, debug=False ):
	return calculatePrecisionRecall(tables, debug)
	# TODO: Machine learning: Passe Thresholds an und für es wieder aus
	

