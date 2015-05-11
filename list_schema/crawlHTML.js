var q = require('q'),
	fs = require('fs'),
	htmlparser = require('htmlparser')
	

readFile('../data/lists_of/List of Archdeacons of East Europe.html')
	.then(function(data){
		// Nur den Inhalt von <body> nehmen (per RegExp) und alle Tabs, Zeilenumbrüche und überflüssige Leerzeichen entfernen
		var data = getDataOfListArticle(data)
		// Parse HTML in JSON
		var bodyElem = parseHTML(data)
		// mw-content-text markiert den Inahlt (ohne Quellenangabe, aber mit Einleitung und das Inhaltsverzeichnis ('toc')
		var contentElem = searchForTag(bodyElem, "div", "mw-content-text")
		// Suche nach allen Auflistung, die nicht in 'toc' liegen
		var lists = searchForTagOccurrences(contentElem, "ul", null, null, ['toc'])
		console.log(lists.length, 'Listen gefunden')
		console.log(JSON.stringify(lists[lists.length-1], null, 2).substring(0, 800))
	}).catch(function(error){
		console.error(error)
	})


function readFile(path) {
	var deferred = q.defer()
	fs.readFile(path, 'utf8', function (err, data) {
		if (err) {
			console.error(err)
			deferred.reject(err)
		} else {
			deferred.resolve(data)
		}
	});
	return deferred.promise
}

function getDataOfListArticle(data) {
	try{
		var regex = /(<body[^>]*>[\s\S]*?<\/body>)/i
		var match = regex.exec(data)
		if (!match) {
			console.log('Looking for start and end of the body tag failed!')
		} else {
			data = match[0]
			data = data.replace(/(\s+)/g, ' ')
			return data
		}
	}catch(e){
		console.error(e)
	}
	return null
}

function parseHTML(data) {
	var handler = new htmlparser.DefaultHandler(function (error, dom) {
		if (error) {
			console.error(error)
			process.exit(1)
		}
	});
	var parser = new htmlparser.Parser(handler)
	parser.parseComplete(data)
	cleanupDom(handler.dom[0]) // Einzelne Leerzeichen werden als eigenes Element gewertet -> Entfernen
	// console.log(JSON.stringify(handler.dom[0], null, 2).substring(0, 1000))
	return handler.dom[0]
}

function cleanupDom(node) {
	if (node.children) {
		for (var i = 0; i < node.children.length; i++) {
			if (node.children[i].raw == ' ') {
				node.children.splice(i, 1)
				i--
			} else {
				cleanupDom(node.children[i])
			}
		}
	}
}

// Parameter 'id' might be null
function searchForTag(node, name, id) {
	if (node.children) {
		for (var i = 0; i < node.children.length; i++) {
			if (node.children[i].name == name && (!id || (node.children[i].attribs && node.children[i].attribs.id == id))) {
				return node.children[i]
			} else {
				var result = searchForTag(node.children[i], name, id)
				if (result) return result
			}
		}
	}
	return null
}

// - Look in the parent element node for elements with a specific tagname (and id)
// - Only search for limited amount of occurrences ('id', 'limit', 'ignoredIDs' might be null)
// - Dont look into elements containing an id listed in ignoredIDs
function searchForTagOccurrences(node, name, id, limit, ignoredIDs, occurrences) {
	if (!occurrences) occurrences = []
	if ((ignoredIDs && node.attribs && contains(ignoredIDs, node.attribs.id))
			|| (limit && occurrences.length >= limit)) {
		return occurrences
	} else {
		if (node.children) {
			for (var i = 0; i < node.children.length; i++) {
				if (node.children[i].name == name && (!id || (node.children[i].attribs && node.children[i].attribs.id == id))) {
					if (limit && occurrences.length >= limit)
						return occurrences
					else 
						occurrences.push(node.children[i])
				} else {
					searchForTagOccurrences(node.children[i], name, id, limit, ignoredIDs, occurrences)
				}
			}
		}
		return occurrences
	}
}

// Faster way than array.indexOf (plus boolean casting)
function contains(a, obj) {
    for (var i = 0; i < a.length; i++) {
        if (a[i] === obj) {
            return true;
        }
    }
    return false;
}