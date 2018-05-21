function init() {
  gapi.load('auth2', initAuth );
}

function initAuth(){
  gapi.auth2.init({
      client_id: '245808396440-muan254t3oh49obnj6v8rk7meb3q6ps8.apps.googleusercontent.com'
  });
}

function onSignIn(googleUser) {
  var profile = googleUser.getBasicProfile();
  console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
  console.log('Name: ' + profile.getName());
  console.log('Image URL: ' + profile.getImageUrl());
  console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.

  var id_token = googleUser.getAuthResponse().id_token;

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/signin');
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
    console.log(xhr.responseText);
    window.location.href = '/redirect';
  };
  xhr.send('username=' + profile.getName() + "&image=" + profile.getImageUrl() + "&email=" + profile.getEmail() + "&id=" + profile.getId());
}

function signOut() {
  gapi.load('auth2', function() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
      console.log('User signed out.');
    });
  });

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/signout');
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
    console.log('logging out...' + xhr.responseText);
    window.location.href = '/redirect';
  };
  xhr.send();
}


function redirect1(){
  setTimeout(redirect2(), 3000)
}

function redirect2(){
  console.log('redirecting');
  window.location.href = '/';
}
