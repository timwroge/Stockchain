(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) {return;}
  js = d.createElement(s); js.id = id;
  js.src = "https://connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

window.fbAsyncInit = function() {
  FB.init({
    appId      : '851500178611688',
    cookie     : true,
    xfbml      : true,
    version    : '{api-version}'
});

FB.AppEvents.logPageView();};

FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
});
