var fs = require('fs'),
    path = require('path')
    q = require('q')

var path = "data/lists_of"

getFilesOfDirectory(path)
.then(function(response){
	console.log(response.length, 'Files')
	for(var i = 0; i < 50; i++) {
		var randomNum = rand(0, response.length)
		console.log(response[rand(0, response.length)])
	}
}).catch(function(err){
	console.error(err)
})


function getFilesOfDirectory(p){
	var deferred = q.defer()
	fs.readdir(p, function (err, files) {
		if (err) {
			deferred.reject(err)
		} else {
			deferred.resolve(files)
		}
	});
	return deferred.promise;
}


function rand(low, high) {
	return Math.round(Math.random() * (high - low) + low)
}
