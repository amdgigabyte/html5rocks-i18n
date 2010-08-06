document.body.innerHTML = "<p>Parent window (gray background)";
document.body.style.backgroundColor = '#ddd';
var iframe = document.createElement('iframe');
iframe.src = 'http://apirocks.com/html5/playground_helper/postMessage_origin.html';
document.body.appendChild(iframe);


window.addEventListener("message", function(e){
  if (e.origin !== "http://apirocks.com" ) { // filter origin for security reasons
    document.getElementById("log").innerHTML = 'The domain you are trying to interact with is not a valid origin.';
  } 
  else {
    // you might as well do some filtering on e.data to be safe
    iframe.style.height = e.data['newHeight'] + 'px';
  }
  // if you were the first time caller you would need to use iframe.contentWindow.postMessage instead
  e.source.postMessage('Iframe resized from the parent to adjust content', 'http://apirocks.com')
}, false);

/*
 If you want to play with the code on the other side of the communication
 just create a page in your domain with calls to
 window.parent.postMessage(e.target.id, "http://savedbythegoog.appspot.com");
 Don't forget to adjust the e.origin checking and the iframe.src 
 on this side to make it work
*/