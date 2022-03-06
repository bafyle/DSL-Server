import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model

actions = [
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

def extract_keypoints(results):
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
#     return np.concatenate([pose, face, lh, rh])
    return np.concatenate([pose, lh, rh])
#     pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
# #     face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
#     lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
#     rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
# #     return np.concatenate([pose, face, lh, rh])
#     return np.concatenate([pose, lh, rh])


def getModel(modelPath):
    model = load_model(modelPath)
    return model


def predict_dslr(model,video_keypoints):
    video_Dimension=[video_keypoints]
    test = np.array(video_Dimension)
    res = model.predict(test)
    result=actions[np.argmax(res[0])]
    return result, np.amax(res)


def predict_for_realtime(frames: list, model):
    video_keypoints = list()
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        for frame in frames:
            _, results = mediapipe_detection(frame, holistic)
            video_keypoints.append(extract_keypoints(results))
        video_keypoints= np.delete(video_keypoints, np.s_[0:132], axis=1)
    return predict_dslr(model, np.array(video_keypoints).mean(0))


def predict_for_single_video_file(temp_file_path, model , model_type, number_of_needed_frames):
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        video_keypoints = list()
        cap = cv2.VideoCapture(temp_file_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total < 30:
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
                    _, results = mediapipe_detection(frame, holistic)
                    video_keypoints.append(extract_keypoints(results))
                    next_pointer=next_pointer+skip
                    next_img=int(next_pointer)
                    counter+=1
        video_keypoints= np.delete(video_keypoints, np.s_[0:132], axis=1)
        if model_type=="ann":
            prediction, predict_proba = predict_dslr(model, np.array(video_keypoints).mean(0))
        else:
            prediction, predict_proba = predict_dslr(model, video_keypoints)
        cap.release()
        return True, prediction, predict_proba


def predict_for_single_image(temp_file_path, model, model_type, unused_arg):
    frame = cv2.imread(temp_file_path)
    keypoints = []
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        _, results = mediapipe_detection(frame, holistic)
        keypoints.append(extract_keypoints(results))
        keypoints = keypoints * 30
        keypoints= np.delete(keypoints, np.s_[0:132], axis=1)
        if model_type=="ann":
            prediction, predict_proba = predict_dslr(model, np.array(keypoints).mean(0))
        else:
            prediction, predict_proba = predict_dslr(model, keypoints)
                

    return True, prediction, predict_proba

