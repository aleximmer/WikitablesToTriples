from bs4 import BeautifulSoup
import codecs

# If a list html doesn't contains a TOC but the function is looking for ul
#		-> set ignoreTOC=true (don't remove the first list form the result set)
def extractLists( tableName, tagName, tagClass=None, ignoreTOC=False, lookRecursive=False):
	# Read html file
	with codecs.open(tableName + '.html', 'r', encoding='UTF-8') as f: # '../data/lists_of/[...]
		htmlCont = f.read()
	
	# Hotfix for n dash (encoding throws UnicodeEncodingError)
	htmlCont = htmlCont.replace('–', '-')
	
	print(htmlCont)
	
	# Parse html content
	soup = BeautifulSoup(htmlCont)

	# Without sources but with the introduction and TOC
	article = soup.find('div', {'id':'mw-content-text'})
	
	if (article):
		# Look for given tag (mostly ul or table)
		lists = article.find_all(tagName, tagClass, lookRecursive)

		# Delete table of contents if detected by BeautifulSoup
		if not ignoreTOC and tagName == 'ul': # TODO: Also check for class == 'toc'
			lists.remove(lists[0])
	
		# Encode special characters
		for i in range(0, len(lists)-1):
			lists[i] = str(lists[i].encode('ISO-8859-2'))
		
		print(str(len(lists)) + ' lists found! \n')
	else:
		print('Failed looking for HTMl content')
	return None
