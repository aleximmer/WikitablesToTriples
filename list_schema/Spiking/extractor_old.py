import hmtl;
#from bs4 import BeautifulSoup
#import codecs
# import HTMLParser
# from chardet import detect

# If a list html doesn't contains a toc but the function is looking for ul
#		-> set ignoreTOC=true (don't remove the first list form the result set)
def extractLists( tableName, tagName, tagClass=None, ignoreTOC=False, lookRecursive=False):
	# Read html file
	# file = open('../data/lists_of/'+tableName+'.html', 'rt')
	# html = file.read()
	# file.close()

	# 1. Try
	with codecs.open('../data/lists_of/List of Archdeacons of Eastern Europe.html','r',encoding='UTF-8') as f:
		text = f.read()
		htmlContent = text.encode('UTF-8')

	# 2. Try: Minus sign equals in HTML &#8211; and &ndash;
	# html_parser = HTMLParser.HTMLParser()
	htmlContent = HTMLenc.unescape(htmlContent)

	# 3. Try: Read in bytes and convert to string
	# file = open('../data/lists_of/List of Archdeacons of Eastern Europe.html', 'rb')
	# html = file.read().decode('ISO-8859-2')

	# 4. Try: Hotfix
	#html = html.replace('–', '-') # Minus sign (ger: Bis-Strich / Gedankenstrich) printed as ÔÇô

	# For testing the representation of a minus sign ( ?–1861 )
	#i = html.find('E. J. Burrow')
	# encoding = lambda x: detect(x)['encoding']
	#print html[i-100 : i+100]
	#print encoding(html[i-100 : i+100])
		
	# Parse html content
	soup = BeautifulSoup(htmlContent)

	# Without sources but with the introduction and TOC
	article = soup.find('div', {'id':'mw-content-text'})
	
	# Look for given tag (mostly ul or table)
	lists = article.find_all(tagName, tagClass, lookRecursive)

	# Delete table of contents if detected by BeautifulSoup
	if not ignoreTOC and tagName == 'ul':
		lists.remove(lists[0])

	# Encode special characters
	# FIXME: ISO-8859-2 = Almu&#241;Úcar  vs  UTF8 = Almu├▒├®car  vs  Original = Almuñécar
	for i in range(0, len(lists)-1):
		lists[i] = str(lists[i].encode('ISO-8859-2'))
		
	print(str(len(lists)) + ' lists found! \n')
	return lists
