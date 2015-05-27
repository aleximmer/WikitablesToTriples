# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import codecs
import json


# Nach TR-Tag suchen (muss THs enthalten)
# 1.) Von dort die THs extrahieren als Header-Array und als JSON ausgeben
# 2.) Spalten in 2D-Array abspeichern und auf Einzigartigkeit überprüfen

# Soup-Element ausgeben:
# Mit Tags (inkl. Links der Entitäten) -> str(obj)
# Nur Plain Text: obj.getText()

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
		raise ValueError('Illegal value for returnType: \'' + returnType + '\' (Allowed: 0, 1 or 2) ')

# Ermittelt mittels dem BeautifulSoup-Package die Kopfzeile der Tabelle und
# gibt alle Header als Array von Soup-Elemente zurück.
# Das Rückgabe-Format kann mit oben gegebenen Konstanten geändert werden.
# Sollte die Kopfzeile nicht gefunden werden oder kein Header vorhanden,
# wirft die Funktion einen ValueError.
def extractTableHead( htmlTable, returnType = RETURN_AS_SOUP_ARRAY() ):
	soup = BeautifulSoup(htmlTable)
	quickView = htmlTable[0:50]+' [...]' 
	
	# Erste Row (TR) egal ob im TBody oder sogar im THead ist die Kopfzeile (Aussage mit Tests überprüfen?)
	header = soup.find('tr')
	if header == None:
		raise ValueError('Can\'t find header row of the given table: \n' + quickView)
	
	colNames = header.findAll('th')
	if (len(colNames) == 0):
		raise ValueError('Can\'t find header row of the given table: \n' + quickView)
	
	return returnWithType( colNames, returnType)


########################################## Key extraction ##########################################

# Ermittelt alle Spalten der Tabelle (ohne die Header-Felder) und überprüft
# diese auf Einzigartigkeit. Sollte keine Spalte dem entsprechen, wird
# ein ValueError geworfen.
# Am Ende wird ein Array von Elementen der Form {'xPos': a, 'entries': c}
# zurückgegeben
def extractUniqueColumns( htmlTable ):
	soup = BeautifulSoup(htmlTable)
	quickView = htmlTable[0:50]+' [...]'
	
	# 1.) Alle Spalten als 2D-Array extrahieren
	body = soup.find('tbody')
	rows = body.findAll('tr')
	rowCount = len(rows)
	colCount = len(rows[0].findAll('td'))
	# Wenn die erste Zeile die Kopfzeile war, hat sie keine td-Tags -> Nächste Zeile nehmen
	if colCount == 0:
		if rowCount > 1:
			colCount = len(rows[1].findAll('td'))
		else:
			raise ValueError('Table doesn\'t contain rows (except the head line): ' + quickView)
	
	# 2D-Array der HTML-Tabelle erzeugen
	# Es wird nur der richtige Plaintext verglichen, aber der ganze HTML-Code gespeichert
	tableData = [[dataField.getText() for dataField in rows[i].findAll('td')] for i in range(rowCount)]
	tableDataRaw = [[str(dataField) for dataField in rows[i].findAll('td')] for i in range(rowCount)]
	
	# 2.) Zu jeder Spalte überprüfen, ob die Einträge einzigartig sind
	uniqueCols = []
	for j in range(colCount):
		# Bereits angesehen Werte zwischenspeichern (für Einzigartigkeits-Check)
		checkedValues = [0 for i in range(rowCount)]
		unique = True
		for i in range(rowCount):
			value = tableData[i][j].strip() # Take plain text and remove alle white spaces from the side
			if value in checkedValues:
				unique = False
				break
			else:
				checkedValues[i] = tableDataRaw[i][j].strip()
		if unique:
			# Alle Einträge der möglichen Key-Spalte als Array speichern
			uniqueCols.append({'xPos': j, 'entries': checkedValues})
	if len(uniqueCols) == 0:
		raise ValueError('Can\'t find any column with unique entries (might be foreing keys)')
	
	return uniqueCols
	
# 3.) TODO: Weitere Techniken (inkl. Bewertung) implementieren:
# 		A) Anzahl der Entitäten (prozentual) ausreichend?
# 		B) Bewertung anhand von Spaltenname (Evidenz oder "Name"),
#			Abstand vom linken Rand und der Anzahl an Entitäten geben
#		C) Bewertung validieren (Erster Kandidat muss prozentual
#			ausreichend vor den anderen Kandidaten liegen)
#	Immer mit einem Array von Elementen mit dem Schema
#	{'xPos': a, 'title': b, 'entries': c} arbeiten (siehe extractUniqueColumns)
#	'title' wird im ausführenden Code nachgereicht (mittels extractTableHead)
	

# Testing:

# Beispiel-Code (HTML einer Tabelle von Wikipedia)
htmlTable = open('./htmlSource.txt').read().replace('\n', ' ')

tableColNames = extractTableHead(htmlTable, RETURN_AS_STRING_ARRAY())
uniqueCols = extractUniqueColumns(htmlTable)

# Führe Title mit Entries und Position zusammen:
uniqueCols = [{'xPos': col['xPos'], 'title': tableColNames[col['xPos']], 'entries': [entry for entry in col['entries']]} for col in uniqueCols]


print(json.dumps(uniqueCols, sort_keys=True, indent=4))



