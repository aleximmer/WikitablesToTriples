function ajaxConnect(action, advertiseID, queryString) {
     // In MySQL &Auml;nderungen speichern, wenn noch aktiv
    var http = null;
    if (window.XMLHttpRequest) {
       http = new XMLHttpRequest();
    }
    else if (window.ActiveXObject) {
       http = new ActiveXObject('Microsoft.XMLHTTP');
    }
    if (http != null) {
        http.open('GET', '' +
        '/ajaxAccess.php?' + queryString, true);
        http.onreadystatechange = catchAnswer;
    }
    $.get("demo_test.asp",function(data,status){
        alert("Data: " + data + "\nStatus: " + status);
	 });
}

function catchAnswer() {
	if (http.readyState == 4) {
		var answer = http.responseText;
		// Behandle Antwort vom XSJS-file
	}
}