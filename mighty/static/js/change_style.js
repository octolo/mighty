function change_style(style) {
    var xhttp = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
    xhttp.open('GET', '/accounts/style/'+style+'/');
    xhttp.timeout = 500;
    xhttp.onload = function(event) {
        data = JSON.parse(xhttp.response); 
        document.getElementsByTagName('body')[0].className = data.style;
    }
    xhttp.send();
}