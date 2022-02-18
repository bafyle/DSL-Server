# Sign Language Django Server

This Django application process the received data (images and videos) from the client and apply any necessary preprocessing before the model prediction.

### Server endpoints
This project has only one endpoint (for now) which is:
~~~
http://host:port/api/upload-media/
~~~
It's used to upload an image or a video to the server and the response of it is the the prediction of the model or and error message, All in JSON format.


### Future Thinking
 * Make all clients send and receiver data using websocket protocol (Django Channels) to avoid any delays from the prediction process and to not delay the request-response cycle.
 * Send the prediction output in JSON format.


### Todo
 * [x] Make sure the model works before integrate it into the server
 * [x] Make a dummy response to insure that websocket works as intended
 * [x] Integrate the model to the server and test it