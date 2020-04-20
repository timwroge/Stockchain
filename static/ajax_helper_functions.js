function createXmlHttp() {
    var xmlhttp;
    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    } else {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    if (!(xmlhttp)) {
        alert("Your browser does not support AJAX!");
    }
    return xmlhttp;
}
recievedRequests = {} ;

// this function converts a simple key-value object to a parameter string.
function objectToParameters(obj) {
    var text = '';
    for (var i in obj) {
        // encodeURIComponent is a built-in function that escapes to URL-safe values
        text += encodeURIComponent(i) + '=' + encodeURIComponent(obj[i]) + '&';
    }
    return text;
}


function postParameters(xmlHttp, target, parameters) {
    if (xmlHttp) {
        xmlHttp.open("POST", target, true); // XMLHttpRequest.open(method, url, async)
        var contentType = "application/x-www-form-urlencoded";
        xmlHttp.setRequestHeader("Content-type", contentType);
        xmlHttp.send(parameters);
    }
}

function sendJsonRequest(parameterObject, targetUrl, callbackFunction) {
    var xmlHttp = createXmlHttp();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4) {
            console.log(xmlHttp.responseText);
            var recievedRequests = JSON.parse(xmlHttp.responseText);
            callbackFunction(recievedRequests, targetUrl, parameterObject);
        }
    };
    console.log(targetUrl);
    console.log(parameterObject);
    postParameters(xmlHttp, targetUrl, objectToParameters(parameterObject));
}

// This can load data from the server using a simple GET request.
function getData(targetUrl, name) {
    let xmlHttp = createXmlHttp();
    xmlHttp.onreadystatechange = function () {
        console.log("Trying to get data");
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            // note that you can check xmlHttp.status here for the HTTP response code
            console.log("Got something!");
            console.log(".. done getting data");
            // check if it is not defined
            recievedRequests[name]  = JSON.parse(xmlHttp.responseText);
            console.log("heres the object;");
        }
    };
    xmlHttp.open("GET", targetUrl, true);
    xmlHttp.send();
}

function showError(msg) {
    let errorAreaDiv = document.getElementById('ErrorArea');
    errorAreaDiv.display = 'block';
    errorAreaDiv.innerHTML = msg;
}

function hideError() {
    let errorAreaDiv = document.getElementById('ErrorArea');
    errorAreaDiv.display = 'none';
}

// use this to clear the values in the "add item" form
function clearItemForm() {
    document.getElementById("item_quantity").value = '';
    document.getElementById("item_title").value = '';
}

// this is called in response to saving list item data.
function itemSaved(result, targetUrl, params) {
    if (result && result.ok) {
        console.log("Saved item.");
        clearItemForm();
        loadItems();
    } else {
        console.log("Received error: " + result.error);
        showError(result.error);
    }
}

// when the list items are loaded from the server, we use this function to
// render them on the page
function generatePointCloud(data, targetUrl) {
    if (data) {
        console.log("Got data " + data);
    } else {
        console.log("Did not get data " + data);
    }
}

function loadPointCloud() {
    console.log("Loading the point cloud");
    myData = getData('/example_point_cloud');
    return myData;
}
