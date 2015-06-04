function isDemand() {
	saveDecission(1);
	alert('Is demand!');
}

function isntDemand() {
	saveDecission(0);
	alert('Is not a demand!');
}

function isntEnglish() {
	saveDecission(0);
	alert('Is not english!');
}

function ignorePost() {
	alert('No decission -> Show next post');
	loadNextPost();
}

//---------------------------------------------------------------//

function loadNextPost() {
	// Content in 'post-content' und Autor in 'post-author'
}

function saveDecission(dec) {
	// Boolean in DB eintragen: 1/True [Behalten], 0/False [Löschen]
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