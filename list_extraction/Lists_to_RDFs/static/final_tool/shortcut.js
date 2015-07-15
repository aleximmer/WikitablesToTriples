$(window).keypress(function(event) {
	switch (event.keyCode) {
	case 89: case 121: // 'y' oder 'Y'
		isDemand();
		break;
	case 78: case 110: // 'n' oder 'N'
		isntDemand();
		break;
	case 76: case 108: // 'l' oder 'L'
		isntEnglish();
		break;
	case 70: case 102: case 39: // 'f' oder 'F' oder Rechtspfeil
		ignorePost();
		break;
	}
});