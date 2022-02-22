# Sign Language Django Server

This Django application process the received data (images and videos) from the client and apply any necessary preprocessing before the model prediction.

### Apps
For now, the server has only two apps, chat app which is an example for django channels and websocket and ML_app which has the MODEL and the prediction function and endpoints.
chat is disabled and will be removed in the future

### Server endpoints
This project has two endpoints (for now) which are:
~~~
http://host:port/api/upload-media/
ws://host:port/real-time/
~~~
http endpoints used to upload an image or a video to the server and the response of it is the the prediction of the model or and error message, All in JSON format.

websocket endpoint is used for sending a stream of frames from opencv and send back to the client the prediction.

### Future Thinking
--


### Todo
 * [x] Make sure the model works before integrate it into the server
 * [x] Make a dummy response to insure that websocket works as intended
 * [x] Integrate the model to the server and test it