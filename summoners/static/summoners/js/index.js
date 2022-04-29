function search_summoner() {
	let region = document.getElementById('btnRegion').textContent;
	let summoner = document.getElementById('summonerName').value;
	window.location.href = "/summoners/" + region + "/" + summoner;
}

function setFocusToTextBox(){
	    document.getElementById("summonerName").focus();
}

window.addEventListener('keyup', function(event) {
	if (event.keyCode === 13) {
		search_summoner();
	}
});

window.onload = setFocusToTextBox();
