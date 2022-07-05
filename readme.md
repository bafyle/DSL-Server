# Dynamic Sign Language Back-end Server

My graduation project back-end server. It serves the incoming request that has a media file attached to it, apply the preprocessing pipeline, and finally return to the client a response with a predicted sign language vocabulary. In addition to a websocket endpoint to provide a real-time prediction.

### Technologies
This server is built using Django Framework and Django channels library.
For now, the server has only one app: ML_app. Which has the model and the prediction process and endpoints.

### Server Endpoints
This project has two endpoints (for now) which are:
~~~
http://host:port/api/upload-media/
ws://host:port/real-time/
~~~
http endpoints used to upload an image or a video to the server and the response of it is the the prediction of the model or and error message, All in JSON format.

ws endpoint (websocket) is used for sending a stream of video frames and send back to the client the prediction.
