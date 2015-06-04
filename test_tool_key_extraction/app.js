

function valResult() {
	selRadio = document.querySelector('input[name="column"]:checked')
	alert(selRadio)
	
	// TODO: saveDecission(colNum)
	// TODO: loadNextPost()
}

//---------------------------------------------------------------//

function loadNextPost() {
	// TODO
}

function saveDecission(colNum) {
	// TODO
}

//---------------------------------------------------------------//

function updateDecisionStatus(status) {
	if (status == 'green') {
		$('#decission-status').attr('class', 'greenDec')
		$('#decission-status').html('Take the selected column')
	} else if (status == 'red') {
		$('#decission-status').attr('class', 'redDec')
		$('#decission-status').html('There is no key column')
	} else {
		$('#decission-status').attr('class', 'noDec')
		$('#decission-status').html('- (Status: '+status+')')
	}
}

function deselectRadioButton() {
	$('input[name="column"]').attr('checked', false)
	updateDecisionStatus('red')
}