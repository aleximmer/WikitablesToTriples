

function evalResult() {
	selRadio = document.querySelector('input[name="column"]:checked')
	// alert(selRadio.value)
	
	// TODO: saveDecission(colNum)
	// TODO: loadNextPost()
}

//---------------------------------------------------------------//

firstTime = true
function loadNextPost() {
	// TODO: Schnittstelle wieder einkommentieren
	
	$.getJSON("/Tables/KeyTest", null)
		.done(function(json) {
			console.log("JSON Data: \n\n" + json)
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
			alert(error)
		});
	/*
	$('.startContainer').hide()
	$('.container').show()
	$('.submit-panel').show()
	*/
}

function receiveJSON(data) {
	// data is a JSON object containing the table in html and
	// results of the key extraction algorithm
	
	// TODO:
	// 0. TableID speichern
	// 1. Im HTML über indexOf vor dem ersten "<tr>" die RadioButton einfügen (Anzahl = count(data['colInfos']))
	//		- Dabei das Ergebnis des Algorithmus direkt markieren (value=id)
	// 2. HTML-Code der Tabelle in $('#table-content') laden (.html(str))
	// 3. Artikel- & Tabellenname in $('#table-source') laden (.html(str))
	// 4. $('#decission-status') updaten -> updateDecisionStatus
}

function saveDecission(colNum) {
	$.ajax({
		method: "GET",
		url: "/table/KeyResult",
		dataType: "json",
		data: {id: "[tableID]", key: None} // or {key: xPos}   [TODO]
	}).done(function() {
			console.log("Result send!")
		})
		.fail(function(jqxhr, textStatus, error) {
			console.log("Request Failed: " + textStatus + ", " + error)
		});
	// TODO: tableID zurückgeben, None or {key: xPos}
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




