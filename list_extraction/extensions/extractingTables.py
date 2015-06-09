# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import codecs
import json
import extensions.inflect as inflect
import math
import sys

# Nach TR-Tag suchen (muss THs enthalten)
# 1.) Von dort die THs extrahieren als Header-Array und als JSON ausgeben
# 2.) Spalten in 2D-Array abspeichern und auf Einzigartigkeit überprüfen

# Soup-Element ausgeben:
# Mit Tags (inkl. Links der Entitäten) -> str(obj)
# Nur Plain Text: obj.getText()

# Engine, um Singular und Plural von Wörtern zu bilden
p = inflect.engine()

# NOT IMPLEMENTED: MIN_ENTITIES_COUNT = 0.4 # Mind. 40% müssen Entities sein, damit die Spalte der Key sein darf

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
	htmlTable = htmlTable.replace("<th ", "<td ")
	
	# TODO: Erkennen ob die erste Zeile wirklich der Header ist oder es keinen gibt
	# Make the first row to a header row (<td> to <th>)
	pos1 = htmlTable.find("<tr")
	pos2 = htmlTable.find("</tr>") + 5
	firstRow = htmlTable[pos1:pos2]
	firstRow = firstRow.replace("<td ", "<th ")
	return htmlTable[:pos1] + firstRow + htmlTable[pos2:]
	

# Benutze BeautifulSoup, um alle Spalten abzuzählen. In der ersten Reihe dürfen td & th stehen
def countAllCols( htmlTable ):
	soup = BeautifulSoup(htmlTable)
	firstRow = soup.find("tr")
	return len(firstRow.findAll("th") + firstRow.findAll("td"))

# Ermittelt alle Spalten der Tabelle (ohne die Header-Felder) und überprüft
# diese auf Einzigartigkeit. Sollte keine Spalte dem entsprechen, wird
# ein ValueError geworfen.
# Am Ende wird ein Array von Elementen der Form {"xPos": a, "entries": c}
# zurückgegeben
def extractUniqueColumns( htmlTable ):
	soup = BeautifulSoup(htmlTable)
	quickView = htmlTable[0:50]+" [...]"
	
	# Um Indexierungsprobleme komplett zu vermeiden TH durch TD ersetzen + THEAD & TBODY löschen
	
	# 1.) Überprüfen ob die Tabelle ein gültiges Format hat
	rowSpan = htmlTable.find("rowspan")
	colSpan = htmlTable.find("colspan")
	if (rowSpan != -1) or (colSpan != -1):
		raise ValueError("Table uses not supported formattings (rowspan or colspan): " + quickView)
	
	# 2.) Alle Spalten als 2D-Array extrahieren
	rows = soup.findAll("tr")
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
	
	# 3.) 2D-Array der HTML-Tabelle erzeugen
	# Es wird nur der richtige Plaintext verglichen, aber der ganze HTML-Code gespeichert
	if firstLineIsHeader:
		#tableData = [[dataField.getText() for dataField in rows[i+1].findAll("td")] for i in range(rowCount)]
		tableDataRaw = [[str(dataField) for dataField in rows[i+1].findAll("td")] for i in range(rowCount)]
	else:
		#tableData = [[dataField.getText() for dataField in rows[i].findAll("td")] for i in range(rowCount)]
		tableDataRaw = [[str(dataField) for dataField in rows[i].findAll("td")] for i in range(rowCount)]
	
	# 4.) Zu jeder Spalte überprüfen, ob die Einträge einzigartig sind (Vergleicht dafür inkl. Tags)
	uniqueCols = []
	for j in range(colCount):
		# Bereits angesehen Werte zwischenspeichern (für Einzigartigkeits-Check)
		checkedValues = [0 for i in range(rowCount)]
		unique = True
		for i in range(rowCount):
			#FIXME: "list index out of range" -> tableData[0] leer -> findAll("td") hat nichts gefunden
			# -> Header-Zeile wurde mitgelesen (soll nicht passieren)
			value = tableDataRaw[i][j].strip() # Take plain text and remove alle white spaces from the side
			if value in checkedValues:
				unique = False
				break
			else:
				checkedValues[i] = tableDataRaw[i][j].strip()
		if unique:
			# Alle Einträge der möglichen Key-Spalte als Array speichern (plain, nicht raw)
			uniqueCols.append({"xPos": j, "entries": [tableDataRaw[x][j] for x in range(rowCount)]})
	if len(uniqueCols) == 0:
		raise ValueError("Can\'t find any column with unique entries (might be foreing keys)")

	# Führe Title mit Entries und Position zusammen (Schema):
	tableColNames = extractTableHead(htmlTable, RETURN_AS_STRING_ARRAY())
	uniqueCols = [{
			"xPos": col["xPos"],
			"title": tableColNames[col["xPos"]],
			"entries": col["entries"],
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
			linksCount = len(links)
			for link in links:
				# Image werden nicht gezählt
				if link.find("img") != None:
					linksCount -= 1
				# Ebenso dürfen es nur Wikipedia-interne Links sein
				elif link["href"][0:5] != "/wiki":
					linksCount -= 1
			if linksCount > 0:
				entityCount += 1
				if linksCount > 1:
					multipleEnts = True
		
		# Bewertung: Maximal 50 Punkte möglich (100% sind Entitäten)
		cols[i]["rating"] = int(math.floor(50 * (entityCount / len(entries))))
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
		# Titel auf den Inhalt "Name" überprüfen
		if "name" in colNames:
			cols[i]["rating"] += 20
		else:
			cols[i]["rating"] += 0
		
		# Titel mit dem Artikelnamen abgleichen
		for word in colNames:
			if word in articleNames:
				# Wenn eines der Wörter auch im Artikelnamen auftaucht, erhöht das das Rating
				# Die gegebene Punktzahl ist von der Wortlänge abhängig (Problematische Wörter
				# wie "in", "the", "of" o.ä. haben dann wenig Einfluss)
				cols[i]["rating"] += max(len(word), 20)
			if p.plural(word) in articleNames:
				# Wenn der Plural trifft, ist es ein wichtigerer Treffer als ein normaler
				cols[i]["rating"] += max(len(word), 20) + 5

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
		addRating = int(math.floor(20 / posVal)) # Hyperbolisch
		cols[i]["rating"] += addRating

# Vergleicht die Ratings der Spalten, um die Key-Spalte zu ermitteln.
# Das größte Rating muss 15% vor dem zweiten liegen. Außerdem müssen
# mind. 40% der Einträge Entitäten sein. Wenn keine Key-Spalte gefunden
# wurde, wird None zurückgegeben (ansonsten das Spaltenelement)
def validateRatings( cols ):
	cols.sort(key=lambda obj: obj["rating"], reverse=True)
	rating1 = cols[0]["rating"]
	if len(cols) > 1:
		rating2 = cols[1]["rating"]
		# Wenn der erste und zweite Platz zu nah sind, ist das Ergebnis nicht eindeutig genug
		if (rating2 / rating1) > 0.85:
			print("Nicht eindeutig genug")
			return None
	
	# Die Entitäten müssen eindeutig sein (Max. eine Entität pro Feld)
	if cols[0]["multipleEntities"]:
		print("Einträge kommen doppelt vor")
		return None
	
	rowCount = len(cols[0]["entries"])
	entityCount = cols[0]["entityCount"]
	# Wenn weniger als 40% der Einträge Entitäten sind, ist die Spalte nicht ausreichend verwertbar
	print(entityCount)
	print(rowCount)
	print(entityCount / rowCount)
	if (entityCount / rowCount) < 0.4:
		print("Zu wenig Links")
		return None
	
	print(cols[0])
	return cols[0]

# Um die Testergebnisse zu visualisieren, werden die Ergebnisse
# der drei Runden als CSV gespeichert
def saveCSVData( roundsResults, cols, round ):
	roundsResults.append([])
	for col in cols:
		roundsResults[round].append(col["rating"])
