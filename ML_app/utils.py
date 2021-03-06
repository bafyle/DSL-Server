from uuid import uuid4
import magic
import logging
import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
import os
import enum
from django.conf import settings

def getModel(modelPath):
    model = load_model(modelPath)
    return model


class ModelType(enum.Enum):
    ANN = 1,
    RNN = 2


MODEL = getModel(os.path.join(settings.BASE_DIR, "model_files/annDSL_Best_ValidationDelete.h5"))
ACTIONS = [
    'Hello','HowAre',
    'Love','Mask',
    'No','Please',
    'Sorry','Thanks',
    'Wear','You'
]

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
    return image, results

def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS) # Draw face connections
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS) # Draw pose connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS) # Draw left hand connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS) # Draw right hand connections

    
def draw_styled_landmarks(image, results):
    # Draw face connections
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS, 
                             mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1), 
                             mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
                             ) 
    # Draw pose connections
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                             ) 
    # Draw left hand connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                             mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                             ) 
    # Draw right hand connections  
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                             mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                             ) 

def extract_keypoints_for_rnn_model(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    # face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    # return np.concatenate([pose, face, lh, rh])
    return np.concatenate([pose, lh, rh])


def extract_keypoints_for_ann_model(results):
    try:
        nose_x=results.pose_landmarks.landmark[0].x
        nose_y=results.pose_landmarks.landmark[0].y
    except:
        nose_x=0
        nose_y=0
    pose = np.array([[res.x-nose_x, res.y-nose_y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    # face = np.array([[res.x-nose_x, res.y-nose_y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    lh = np.array([[res.x-nose_x, res.y-nose_y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x-nose_x, res.y-nose_y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    # return np.concatenate([pose, face, lh, rh])
    return np.concatenate([pose, lh, rh])






def is_action(results):

# chech if there are any hands
    if not results.left_hand_landmarks and not results.right_hand_landmarks:
        return False

    # get the y axis for each keypoint in the hand
    # if no hand then give the keypoint large value (10)
    lh = np.array([[res.y] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.full((21), 10)
    rh = np.array([[res.y] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.full((21), 10)



    # Get the max value in each hand
    # Hint: A large value means it goes down the image.
    maxval_lh = np.max(lh)
    maxval_rh = np.max(rh)

    # get the y axis values for left_hip and right_hip
    left_hip=results.pose_landmarks.landmark[23].y
    right_hip=results.pose_landmarks.landmark[24].y

    # get the minimum on
    # Hint: A minimum value means it goes up the image.
    min_hip=min(left_hip,right_hip)

    # check if the minimmum value from the hands is greater than the hip
    # if true it means all hands are below the hip
    if min(maxval_lh,maxval_rh) > min_hip :
        return False

    return True





def predict_dslr(model,video_keypoints):
    video_dimensions=[video_keypoints]
    video_dimensions_nparray = np.array(video_dimensions)
    res = model.predict(video_dimensions_nparray)
    result=ACTIONS[np.argmax(res[0])]
    return result, np.amax(res)


def predict_for_realtime(frames: list, model):
    video_keypoints = list()
    are_actions = []
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        for frame in frames:
            _, results = mediapipe_detection(frame, holistic)
            are_actions.append(is_action(results))
            video_keypoints.append(extract_keypoints_for_ann_model(results))
        if are_actions.count(False) > len(frames) / 1.5:
            return "No Action", 100
        video_keypoints= np.delete(video_keypoints, np.s_[0:132], axis=1)
    return predict_dslr(model, np.array(video_keypoints).mean(0))


def predict_for_single_video_file(temp_file_path, model , model_type: ModelType, number_of_needed_frames):
    video_keypoints = list()
    cap = cv2.VideoCapture(temp_file_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    are_actions = []
    if total < number_of_needed_frames:
        cap.release()
        return False, "attached video duration is short"
    skip=total/number_of_needed_frames
    next_img=0
    next_pointer=0
    counter=0
    for i in range(0,total):
        if counter==number_of_needed_frames:
            break
        else:
            _, frame = cap.read()
            if i == next_img:
                with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
                    _, results = mediapipe_detection(frame, holistic)
                are_actions.append(is_action(results))
                video_keypoints.append(extract_keypoints_for_ann_model(results))
                next_pointer=next_pointer+skip
                next_img=int(next_pointer)
                counter+=1
    if are_actions.count(False) > number_of_needed_frames /  1.2:
        return True, "No Action", 1
    video_keypoints= np.delete(video_keypoints, np.s_[0:132], axis=1) # removing pose estimation
    if model_type==ModelType.ANN:
        prediction, predict_proba = predict_dslr(model, np.array(video_keypoints).mean(0))
    elif model_type == ModelType.RNN:
        prediction, predict_proba = predict_dslr(model, video_keypoints)
    cap.release()
    return True, prediction, predict_proba


def predict_for_single_image_file(temp_file_path, model, model_type: ModelType, number_of_needed_frames):
    frame = cv2.imread(temp_file_path)
    keypoints = []
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        _, results = mediapipe_detection(frame, holistic)
        if is_action(results): 
            keypoints.append(extract_keypoints_for_ann_model(results)) 
            keypoints = keypoints * number_of_needed_frames
            keypoints= np.delete(keypoints, np.s_[0:132], axis=1) # removing pose estimation
            if model_type == ModelType.ANN:
                prediction, predict_proba = predict_dslr(model, np.array(keypoints).mean(0))
            elif model_type == ModelType.RNN:
                prediction, predict_proba = predict_dslr(model, keypoints)
        else:
            prediction="No Action"
            predict_proba =1

    return True, prediction, predict_proba


def get_random_file_name_and_path():
    file_name = str(uuid4())
    return file_name, settings.MEDIA_ROOT + file_name

def get_file_type(uploaded_file):
    return magic.from_buffer(uploaded_file.read(2048), mime=True).split("/")[0]


def save_file(temp_file_path: str, uploaded_file):
    with open(temp_file_path, "wb") as new_file:
        for line in uploaded_file:
            new_file.write(line)
            new_file.flush()

def delete_file(temp_file_path: str):
    try:
        os.remove(temp_file_path)
    except (FileNotFoundError, PermissionError) as e:
        logging.warning(f"file: {temp_file_path} was not deleted due to {e.strerror}")