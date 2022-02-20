import magic
import uuid
from django.http import (
    HttpRequest,
    JsonResponse
)
from django.conf import settings
from .utils import (
    getModel,
    predict_image,
    predict_video
)
import os
import logging

MODEL = getModel(os.path.join(settings.BASE_DIR, "model_files/DSL_Best_Validation_99T_99V.h5"))

file_type_prediction_dict = {"video": predict_video, "image": predict_image}

def upload_media_view(request: HttpRequest):
    if request.method != "POST":
        return JsonResponse({"message": "bad", "description":"method not allowed"}, status=405)

    if (uploaded_file := request.FILES.get("file")) is None:
        return JsonResponse({"message":"bad", "description":"no media attached"})
    
    temp_file_name = str(uuid.uuid4())
    temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_name)

    uploaded_file_type = magic.from_buffer(uploaded_file.read(2048), mime=True).split("/")[0]

    if (prediction_function := file_type_prediction_dict.get(uploaded_file_type)) is None:
        return JsonResponse({"message":"bad", "description":"corrupted or unsupported file"})
        
    with open(temp_file_path, "wb") as new_file:
        for line in uploaded_file:
            new_file.write(line)
            new_file.flush()
    
    output = prediction_function(temp_file_path, MODEL)
    
    try:
        os.remove(temp_file_path)
    except (FileNotFoundError, PermissionError) as e:
        logging.warning(f"file: {temp_file_name} was not deleted due to {e.strerror}")
    
    if output[0]:
        return JsonResponse({"message":"good", "prediction":output[1], "predict_proba":str(output[2])})
    return JsonResponse({"message":"bad", "description":output[1]})



