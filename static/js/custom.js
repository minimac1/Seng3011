function init() {
  gapi.load('auth2', function() { console.log('gapi loaded') });
  gapi.auth2.init({client_id: '245808396440-muan254t3oh49obnj6v8rk7meb3q6ps8.apps.googleusercontent.com'}})
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
    console.log('Signed in as: ' + xhr.responseText);
  };
  xhr.send('username=' + profile.getName());
  location.reload();
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
  };
  xhr.send();
  location.reload();
}
