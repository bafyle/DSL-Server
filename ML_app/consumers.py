import json
import cv2
from .utils import(
    MODEL,
    predict_for_realtime
) 
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer


class RealtimeConsumer(AsyncWebsocketConsumer):

    # handshaking for incoming connection
    async def connect(self):
        self.buffer = [] # initialize a buffer for the stream
        await self.accept() # accept the connection
    
    # Do something when client disconnects from websocket
    async def disconnect(self, close_code):
        self.buffer.clear()
    
    # Receive message from WebSocket
    async def receive(self, bytes_data):
        """
        Upon receiving a frame from the client, we decode that frame
        and store it in a buffer
        when the buffer has 30 frames, we begin our prediction process
        and send the model prediction to the client
        """
        if len(self.buffer) < 30:
            self.buffer.append(self._decode_opencv_image(bytes_data))
        
        if len(self.buffer) == 30:

            prediction, predict_proba = predict_for_realtime(self.buffer, MODEL)

            await self.send(text_data=json.dumps({
                'prediction': prediction,
                "predict_proba":str(predict_proba)
            }))
            self.buffer.clear()


    def _decode_opencv_image(self, img_stream, cv2_img_flag=cv2.IMREAD_UNCHANGED):
        img_array = np.asarray(bytearray(img_stream), dtype=np.uint8)
        data = cv2.imdecode(img_array, cv2_img_flag)
        return data
