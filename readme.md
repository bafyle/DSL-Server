# Sign Language Django Server

This Django application process the received data (images and videos) from the client and apply any necessary preprocessing before the model prediction.

### Future Thinking
 * Make all clients send and receiver data using websocket protocol (Django Channels) to avoid any delays from the prediction process and to not delay the request-response cycle.
 * Send the prediction output in JSON format.


### Todo
 * [ ] Make sure the model works before integrate it into the server
 * [ ] Make a dummy response to insure that websocket works as intended
 * [ ] Integrate the model to the server and test it