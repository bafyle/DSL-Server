import magic
import uuid
from django.http import HttpRequest, JsonResponse
from django.conf import settings
from .utils import (
    getModel,
    predict_image,
    predict_video
)
import cv2
import os

MODEL = getModel("./ML/DSL_Best_Validation_99T_99V.h5")

def upload_file_view(request: HttpRequest):

    if request.method == "POST":
        if (uploaded_file:=request.FILES.get("file")):
            temp_file_path = settings.MEDIA_ROOT + str(uuid.uuid4())
            uploaded_file_type, extension = magic.from_buffer(uploaded_file.read(2048), mime=True).split("/")
            with open(temp_file_path, "wb") as new_file:
                for line in uploaded_file:
                    new_file.write(line)
                    new_file.flush()
            new_file.close()
            output = predict_video(temp_file_path, MODEL) if uploaded_file_type == "video" else predict_image(temp_file_path, MODEL)
            try:
                os.remove(temp_file_path)
            except (FileNotFoundError, PermissionError) as e:
                print(e)
            if output[0]:
                return JsonResponse({"message":"good", "prediction":output[1], "predict_proba":str(output[2])})
            return JsonResponse({"message":"bad", "description":output[1]})
        return JsonResponse({"message":"bad", "description":"no files attached"})
    return JsonResponse({"message": "bad", "description":"method not allowed"}, status=405)


