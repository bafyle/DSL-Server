import magic
import uuid
from django.http import HttpRequest, JsonResponse
from django.conf import settings
from .utils import (
    getModel,
    mediapipe_detection,
    mp_holistic,
    extract_keypoints,
    predict_dslr
)
import cv2
import os

MODEL = getModel("./ML/DSL_Best_Validation_99T_99V.h5")

def upload_file_view(request: HttpRequest):

    if request.method == "POST":
        if (uploaded_file:=request.FILES.get("file")):
            temp_file_path = settings.MEDIA_ROOT + str(uuid.uuid4())
            uploaded_file_type, extension = magic.from_buffer(uploaded_file.read(2048), mime=True).split("/")
            if uploaded_file_type == "video":
                with open(temp_file_path, "wb") as new_file:
                    for line in uploaded_file:
                        new_file.write(line)
                        new_file.flush()
                new_file.close()
                with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
                    cap = cv2.VideoCapture(temp_file_path)
                    video_keypoints = list()
                    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    if total >= 30:
                        targetFrames = 30
                        for _ in range(targetFrames):
                            _, frame = cap.read()
                            _, results = mediapipe_detection(frame, holistic)
                            video_keypoints.append(extract_keypoints(results))
                        prediction, predict_proba = predict_dslr(MODEL, video_keypoints)
                    else:
                        return JsonResponse({"message": "bad", "description": "attached video is not long enough"})
                
            elif uploaded_file_type == "image":
                pass
            cap.release()
            try:
                os.remove(temp_file_path)
            except (FileNotFoundError, PermissionError) as e:
                print(e)
                
            return JsonResponse({"message":"good", "prediction":prediction, "predict_proba": str(predict_proba)}) # return the prediction to the client
        return JsonResponse({"message":"bad", "description":"no files attached"})
    return JsonResponse({"message": "bad", "description":"method not allowed"}, status=405)


