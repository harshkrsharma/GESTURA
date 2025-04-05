# Initialize Mediapipe
import mediapipe as mp
import cv2
import numpy as np
import json
import os
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import time
import pyautogui
import subprocess
import time
import mediapipe as mp
import cv2
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

from gesture_actions import GESTURE_ACTIONS

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

TARGET_WIDTH = 320
TARGET_HEIGHT = 240
cap = cv2.VideoCapture(2)
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# File to store gestures
GESTURE_FILE = "gestures.json"
COOLDOWN_TIME = 1  # Cooldown time before detecting the next gesture

# Define key landmarks to check
keypoints_to_check = [0, 1, 4, 5, 8, 9, 12, 13, 16, 17, 20]
 

# Load existing gestures if available
if os.path.exists(GESTURE_FILE):
    with open(GESTURE_FILE, "r") as f:
        gesture_dict = json.load(f)
        # Convert each stored frame into a numpy array
        gesture_dict = {
            k: {
                "start": np.array(v["start"], dtype=np.float32),
                "mid1": np.array(v["mid1"], dtype=np.float32),
                "mid2": np.array(v["mid2"], dtype=np.float32),
                "end": np.array(v["end"], dtype=np.float32)
            }
            for k, v in gesture_dict.items()
        }
else:
    gesture_dict = {}

# Variables to track sequential matching
pending_gesture = None  # The gesture name matched at "start"
frame_stage = 0         # 0: start, 1: mid1, 2: mid2, 3: end
last_detection_time = 0
gesture_keyframes={}

# New: Stage timeout (in seconds)
STAGE_TIMEOUT = 5
stage_start_time = None  # Record when the current stage started

def normalize_landmarks(landmarks):
    """Normalize landmarks by centering and scaling relative to the entire hand size."""
    min_x, min_y, _ = np.min(landmarks, axis=0)
    max_x, max_y, _ = np.max(landmarks, axis=0)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    centered_landmarks = landmarks - np.array([center_x, center_y, 0])
    hand_width, hand_height = max_x - min_x, max_y - min_y
    scale = max(hand_width, hand_height)
    if scale > 0:
        centered_landmarks /= scale
    return centered_landmarks

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    current_time = time.time()

    # Optional cooldown: skip processing if too soon after last detection
    if current_time - last_detection_time < COOLDOWN_TIME:
        cv2.imshow("Sign Prediction", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        continue

    # If we're in a sequence (frame_stage > 0) but too much time has passed, reset sequence.
    if frame_stage > 0 and stage_start_time is not None:
        if current_time - stage_start_time > STAGE_TIMEOUT:
            print("⏰ Stage timed out. Resetting sequence.")
            pending_gesture = None
            frame_stage = 0
            stage_start_time = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = np.array([(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark],
                                 dtype=np.float32)
            if landmarks.shape[0] < max(keypoints_to_check):
                continue  # Incomplete detection; skip this frame

            normalized_landmarks = normalize_landmarks(landmarks)
            normalized_keypoints = normalized_landmarks[keypoints_to_check]
            frame_sequence = ["start", "mid1", "mid2", "end"]

            # For the first stage, if no sequence is started, try to match "start"
            if frame_stage == 0:
                for gesture_name, frames in gesture_dict.items():
                    keyframe_points = frames["start"].reshape(-1, 3)
                    if keyframe_points.shape != normalized_keypoints.shape:
                        continue
                    distance, _ = fastdtw(keyframe_points, normalized_keypoints, dist=euclidean)
                    if distance < 1:
                        pending_gesture = gesture_name
                        frame_stage = 1
                        stage_start_time = current_time  # Start timing this stage
                        print(f"🟢 'Start' frame matched for '{gesture_name}'!")
                        break

            # For subsequent stages, use the pending gesture's corresponding frame
            elif pending_gesture:
                stage_name = frame_sequence[frame_stage]
                keyframe_points = gesture_dict[pending_gesture][stage_name].reshape(-1, 3)
                if keyframe_points.shape == normalized_keypoints.shape:
                    distance, _ = fastdtw(keyframe_points, normalized_keypoints, dist=euclidean)
                    if distance < 1:
                        print(f"🟢 '{stage_name.capitalize()}' frame matched for '{pending_gesture}'!")
                        frame_stage += 1
                        stage_start_time = current_time  # Reset timer for next stage
                        if frame_stage == 3:  # All stages matched
                            print(f"✅ Detected Sign: {pending_gesture}")
                            try:
                                GESTURE_ACTIONS[pending_gesture]()
                            except Exception as e:
                                print(f"❌ Error executing action: {e}")
                            last_detection_time = current_time
                            pending_gesture = None
                            frame_stage = 0  # Reset for next gesture detection
                            stage_start_time = None
                            break  # Stop processing further for this hand

    # Handle key presses to record frames or quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('1'):
        if results.multi_hand_landmarks:
            gesture_keyframes["start"] = normalize_landmarks(landmarks)[keypoints_to_check].copy()
            print("✅ Start frame recorded!")
    elif key == ord('2'):
        if results.multi_hand_landmarks:
            gesture_keyframes["mid1"] = normalize_landmarks(landmarks)[keypoints_to_check].copy()
            print("✅ Mid1 frame recorded!")
    elif key == ord('3'):
        if results.multi_hand_landmarks:
            gesture_keyframes["mid2"] = normalize_landmarks(landmarks)[keypoints_to_check].copy()
            print("✅ Mid2 frame recorded!")
    elif key == ord('4'):
        if results.multi_hand_landmarks:
            gesture_keyframes["end"] = normalize_landmarks(landmarks)[keypoints_to_check].copy()
            print("✅ End frame recorded!")
            gesture_name = input("Enter the word for this sign: ")
            gesture_dict[gesture_name] = gesture_keyframes.copy()
            with open(GESTURE_FILE, "w") as f:
                json.dump(
                    {k: {frame: v.tolist() for frame, v in frames.items()} for k, frames in gesture_dict.items()},
                    f
                )
            print(f"📁 Sign '{gesture_name}' saved permanently!")
    elif key == ord('q') or key == 27:
        break

    cv2.imshow("Sign Prediction", frame)

cap.release()
cv2.destroyAllWindows()
