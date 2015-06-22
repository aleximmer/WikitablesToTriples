/*
Initial script used to save htmls to storage (using the server)
*/
var fs = require('fs')
var request = require('request')
var LineByLine = require('line-by-line')

// Function to extract html from url and save as file
var retrieveURL = function(url, name) {
	request
  		.get(url)
  		.on('error', function(err) {
    		console.log(err)
  		})
  		.pipe(fs.createWriteStream('./data/lists_of/' + name + '.html'));
};

var lr = new LineByLine('./data/ListOf.txt');

// error handling during line by line file reading
lr.on('error', function(e) {
	console.log('Line Read Error');
});

// get url and name per dataset (each line represents one dataset)
lr.on('line', function(line) {
	
	// get wikipedia link
	var posLeft = line.indexOf('http://en.wikipedia.org/wiki'),
		posRight = line.indexOf('?oldid='),
		url = line.substring(posLeft, posRight);
	
	// ...."List of xyz".... -> Split and get middle string by index
	// replace '/' to avoid adding directories
	var subLine = line.split('"')[1].replace('/', '-');

	// few sets containing 'List of' which aren´t lists are filtered
	// e.g. see http://en.wikipedia.org/wiki/Disability/List_of_impairments
	// maybe apply later...
	retrieveURL(url, subLine);

});

lr.on('end', function() {
	console.log('Extraction finished');
});