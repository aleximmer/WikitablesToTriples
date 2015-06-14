# -*- coding: utf-8 -*-


import sys
import extractingTables_api

# Nach TR-Tag suchen (muss THs enthalten)
# 1.) Von dort die THs extrahieren als Header-Array und als JSON ausgeben
# 2.) Spalten in 2D-Array abspeichern und auf Einzigartigkeit überprüfen

# Soup-Element ausgeben:
# Mit Tags (inkl. Links der Entitäten) -> str(obj)
# Nur Plain Text: obj.getText()

############################################# Testing ##############################################

def test( fileName ):
	# Open HTML file
	htmlTable = open('Testing/'+fileName).read().replace('\n', ' ')
	
	# Extract articleName (and tableTitle) by fileName
	parts = fileName.split('_')
	articleName = parts[0]
	if len(parts) > 2:
		tableTitle = parts[2].split('.')[0]
	else:
		tableTitle = None
	print('Testing: '+articleName)
	
	# Rating:
	# Extracting and rating columns
	roundsResults = []
	
	try:
		# Rating:
		# Fix <th> tags because <th> is used in different ways:
		htmlTable = fixTableHeaderTagsForOutput(htmlTable)

		# Extracting and rating columns
		uniqueCols = extractUniqueColumns(htmlTable)

		# Zähle die Entities pro Spalte
		countEntities(uniqueCols)
		saveCSVData(roundsResults, uniqueCols, 0)
		
		# Kommt der Artikelname oder das Wort 'Name' im Spaltenname vor
		valuateByName(uniqueCols, articleName)
		saveCSVData(roundsResults, uniqueCols, 1)

		# Umso weiter links, umso wertvoller ist die Spalte
		valuateByPosition(uniqueCols)
		saveCSVData(roundsResults, uniqueCols, 2)

		# Validiere die Bewertungen der Spalten
		keyCol = validateRatings(uniqueCols)
		
		if keyCol != None:
			keyCol = keyCol['xPos']
		else:
			print('Can\'t extract a significant single key column')
			keyCol = -1
	except Exception as e:
		# Error caused by wrong html format or unsupported html encoding 
		keyCol = -1
		uniqueCols = []
		colCount = countAllCols(htmlTable)

	# Ausgabe:
	if keyCol == None or ((len(sys.argv) > 1) and ('-showCSV' in sys.argv)):
		# Zeige die Bewertungsergebnisse der einzelnen Runden im CSV-Format:
		roundsResultsAsCSV = '"";"Runde 1"; "Runde 2"; "Runde 3"\n'
		for i in range(len(roundsResults[0])):
			roundsResultsAsCSV += '"'+uniqueCols[i]['title']+'";"'+str(roundsResults[0][i])+'";"'+str(roundsResults[1][i])+'";"'+str(roundsResults[2][i])+'"\n'
		roundsResultsAsCSV = roundsResultsAsCSV[:-1] # Letzten Zeilenumbruch entfernen
		print(roundsResultsAsCSV)
	else:
		fieldCount = len(keyCol['entries'])
		keyCol['fieldCount'] = fieldCount
		if fieldCount > 100:
			keyCol['entries'] = keyCol['entries'][:100]
		print(json.dumps(keyCol, sort_keys=True, indent=4))

if (len(sys.argv) > 1) and (sys.argv[1][-4:] == '.txt'):
	test(sys.argv[1])
else:
	test('List of post-1692 Anglican parishes in the Province of Maryland_1.txt')