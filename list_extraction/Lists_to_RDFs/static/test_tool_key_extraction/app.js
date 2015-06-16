

function evalResult() {
	selRadio = $('input[name="column"]:checked')
	saveDecission(selRadio.length > 0 ? selRadio.attr('value') : -1)
	loadNextPost()
}

//---------------------------------------------------------------//

firstTime = true
tryCounter = 0
function loadNextPost() {
	$.getJSON("/Tables/KeyTest", null)
		.done(function(json) {
			tryCounter = 0
			console.log("Received Table Data:")
			console.log(json)
			console.log(json['tableID'])
			receiveJSON(json)
			if (firstTime) {
				firstTime = false
				$('.startContainer').hide()
				$('.container').show()
				$('.submit-panel').show()
			}
		})
		.fail(function(jqxhr, textStatus, error) {
			console.log("Request Failed: " + textStatus + ", " + error)
			if (++tryCounter > 5) {
				alert('Request failed for five times!')
			} else {
				loadNextPost()
			}
			// alert(error)
		});
}

var currentTableID = "-1";
function receiveJSON(data) {
	// data is a JSON object containing the table in html and
	// results of the key extraction algorithm
	
	// Scheme: data = {'tableID': table.id, 'tableName': table.title, 'articleName': articleName,
	//					'tableHTML': htmlTable, 'keyCol': keyCol, 'colInfos': uniqueCols}

	// 0. TableID speichern
	currentTableID = data['tableID']
	// 1. Im HTML über indexOf vor dem ersten "<tr>" die RadioButton einfügen (Anzahl = count(data['colInfos']))
	//		- Dabei das Ergebnis des Algorithmus direkt markieren (value=id)
	var pos = data['tableHTML'].search(/<tr[^>]*>/)
	if (pos == -1) {
		throw "Table HTML code doesn't contain a <tr> tag."
	}
	var radioButtonRow = ""
	var len = parseInt(data['colCount'])
	
	// Collect indexes of all unique columns
	var uniqueColIndexes = []
	for(var i = 0; i < len; i ++) {
		// Check if column index is listed in colInfos
		for(var j = 0; j < data['colInfos'].length; j++) {
			if (i == data['colInfos'][j]['xPos']) {
				uniqueColIndexes.push(i)
			}
		}
	}
	
	for(var i = 0, uniqueID = 0; i < len; i++) {
		var ratingStr = ''
		if (uniqueColIndexes.indexOf(i) != -1) {
			ratingStr = '<sub>('+data['colInfos'][uniqueID++]['rating']+')</sub>'
		}
		
		radioButtonRow += '<td><input type="radio" name="column" value="'+i+'" onclick="updateDecisionStatus(\'green\')" ' +
							((data['keyCol'] && data['keyCol']['xPos'] == i) ? 'checked="checked"' : '') + '/>' +
							ratingStr + '</td>'
	}
	data['tableHTML'] = data['tableHTML'].slice(0, pos) + "<tr>" + radioButtonRow + "</tr>" + data['tableHTML'].slice(pos)
	// 2. HTML-Code der Tabelle in $('#table-content') laden
	$('#table-content').html('<button id="deselect-radio" onclick="deselectRadioButton()">Deselect radio button (r)</button>'
				+ data['tableHTML'])
	// 3. Artikel- & Tabellenname in $('#table-source') laden
	$('#table-source').html(
			'<b>' + data['articleName'] + '</b>' +
			(data['tableName'] != 'None' ? ' > <b>' + data['tableName'] + '</b>' : ''))
	// 4. $('#decission-status') updaten -> updateDecisionStatus
	if (data['keyCol'] != null && data['keyCol'] != -1) {
		$('input[name="column"][value="'+data['keyCol']+'"]').attr("checked","checked")
		updateDecisionStatus('green')
	} else {
		updateDecisionStatus('red')
	}
}

function saveDecission(colNum) {
	$.ajax({
		method: "GET",
		url: "/Tables/KeyResult",
		dataType: "json",
		data: {id: currentTableID, key: (colNum+"")} // might be -1
	}).done(function() {
			console.log("Result send!")
		})
		.fail(function(jqxhr, textStatus, error) {
			console.log("Request Failed: " + textStatus + ", " + error)
		});
}

//---------------------------------------------------------------//

function updateDecisionStatus(status) {
	if (status == 'green') {
		enableDeselector()
		$('#decission-status').attr('class', 'greenDec')
		$('#decission-status').html('Take the selected column')
	} else if (status == 'red') {
		$('#decission-status').attr('class', 'redDec')
		$('#decission-status').html('There is no single key column')
	} else {
		$('#decission-status').attr('class', 'noDec')
		$('#decission-status').html('- (Status: '+status+')')
	}
}

function enableDeselector() {
	$('#deselect-radio').attr('disabled', false)	
}

function deselectRadioButton() {
	$('#deselect-radio').attr('disabled', true)
	$('input[name="column"]').attr('checked', false)
	updateDecisionStatus('red')
}




