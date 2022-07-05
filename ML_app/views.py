from django.http import (
    HttpRequest,
    JsonResponse
)
from django.conf import settings
from django.shortcuts import render
from .utils import (
    MODEL,
    delete_file,
    predict_for_single_image_file,
    predict_for_single_video_file,
    save_file,
    get_file_type,
    get_random_file_name_and_path,
    delete_file,
    ModelType
)

FILE_TYPE_PREDICTION_FUNCTIONS = {"video": predict_for_single_video_file, "image": predict_for_single_image_file}


def upload_media_view(request: HttpRequest):
    """
    Regular django view method that only accept post methods with an image attached to the request.
    It returns a json object that tells if there any errors with the attached file, request method
    or something with the model. The json object also has a the output of the model if all the previous was good
    """
    if request.method != "POST":
        return JsonResponse({"message": "bad", "description":"method not allowed"}, status=405)

    if (uploaded_file := request.FILES.get("file")) is None:
        return JsonResponse({"message":"bad", "description":"no media attached"})
    
    temp_file_name, temp_file_path = get_random_file_name_and_path()
    uploaded_file_type = get_file_type(uploaded_file)

    if (prediction_function := FILE_TYPE_PREDICTION_FUNCTIONS.get(uploaded_file_type)) is None: # if file is not supported
        return JsonResponse({"message":"bad", "description":"corrupted or unsupported file"})
        
    # save the file
    save_file(temp_file_path, uploaded_file)
    
    # predicting what sign is in the uploaded file
    model_output = prediction_function(temp_file_path, MODEL, ModelType.ANN, 30)
    
    # remove the saved file
    delete_file(temp_file_path)
    
    if model_output[0]:
        return JsonResponse({"message":"good", "prediction":model_output[1], "predict_proba":str(model_output[2])})
    return JsonResponse({"message":"bad", "description":model_output[1]})


def stream_view(request: HttpRequest):
    return render(request, "ML_app/stream_demo.html")
