import json
from channels.generic.websocket import AsyncWebsocketConsumer

import cv2
from . import utils
import os
import numpy as np
from django.conf import settings

MODEL = utils.getModel(os.path.join(settings.BASE_DIR, "model_files/DSL_Best_Validation_99T_99V.h5"))

class StreamConsumer(AsyncWebsocketConsumer):

    # handshaking for incoming connection
    async def connect(self):
        self.buffer = []
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
            self.buffer.append(self.decode_opencv_image(bytes_data))
            # await self.send(text_data=json.dumps({"frame":"received"}))
        
        if len(self.buffer) == 30:

            prediction, predict_proba = utils.predict_for_realtime(self.buffer, MODEL)

            await self.send(text_data=json.dumps({
                'prediction': prediction,
                "predict_proba":str(predict_proba)
            }))
            self.buffer.clear()


    def decode_opencv_image(self, img_stream, cv2_img_flag=0):
        img_array = np.asarray(bytearray(img_stream), dtype=np.uint8)
        data = cv2.imdecode(img_array, cv2_img_flag)
        return data