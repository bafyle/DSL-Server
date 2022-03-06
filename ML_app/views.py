import magic
import uuid
from django.http import (
    HttpRequest,
    JsonResponse
)
from django.conf import settings
from django.shortcuts import render
from .utils import (
    MODEL,
    predict_for_single_image_file,
    predict_for_single_video_file
)
import os
import logging


file_type_prediction_functions = {"video": predict_for_single_video_file, "image": predict_for_single_image_file}


def upload_media_view(request: HttpRequest):
    """
    This view get a post request with a file, the attached
    file must be a video or an image of some sort.
    The response of this view is a json object that has a message
    which tells if the prediction process was good or bad with
    a description of if the process was not successful
    """
    if request.method != "POST":
        return JsonResponse({"message": "bad", "description":"method not allowed"}, status=405)

    if (uploaded_file := request.FILES.get("file")) is None:
        return JsonResponse({"message":"bad", "description":"no media attached"})
    
    temp_file_name = str(uuid.uuid4())
    temp_file_path = settings.MEDIA_ROOT + temp_file_name

    uploaded_file_type = magic.from_buffer(uploaded_file.read(2048), mime=True).split("/")[0] # get the file type

    if (prediction_function := file_type_prediction_functions.get(uploaded_file_type)) is None: # if file is not supported
        return JsonResponse({"message":"bad", "description":"corrupted or unsupported file"})
        
    # save the file
    with open(temp_file_path, "wb") as new_file:
        for line in uploaded_file:
            new_file.write(line)
            new_file.flush()
    
    # prediction what sign it is in that file
    output = prediction_function(temp_file_path, MODEL, "ann", 30)
    
    # remove the saved file
    try:
        os.remove(temp_file_path)
    except (FileNotFoundError, PermissionError) as e:
        logging.warning(f"file: {temp_file_name} was not deleted due to {e.strerror}")
    
    if output[0]:
        return JsonResponse({"message":"good", "prediction":output[1], "predict_proba":str(output[2])})
    return JsonResponse({"message":"bad", "description":output[1]})


def stream_view(request: HttpRequest):
    return render(request, "ML_app/stream_demo.html")
