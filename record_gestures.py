import cv2
import json
import os
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk

# Initialize Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

GESTURE_FILE = "gestures.json"
keypoints_to_check = [0, 1, 4, 5, 8, 9, 12, 13, 16, 17, 20]

gesture_dict = {}
if os.path.exists(GESTURE_FILE):
    with open(GESTURE_FILE, "r") as f:
        gesture_dict = json.load(f)

cap = cv2.VideoCapture(2)
current_gesture = {}

def normalize_landmarks(landmarks):
    min_x, min_y, _ = np.min(landmarks, axis=0)
    max_x, max_y, _ = np.max(landmarks, axis=0)
    center_x, center_y = (min_x + max_x) / 2, (min_y + max_y) / 2
    centered_landmarks = landmarks - np.array([center_x, center_y, 0])
    scale = max(max_x - min_x, max_y - min_y)
    if scale > 0:
        centered_landmarks /= scale
    return centered_landmarks

def capture_frame(stage):
    global current_gesture
    ret, frame = cap.read()
    if not ret:
        return
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = np.array([(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark], dtype=np.float32)
            normalized_landmarks = normalize_landmarks(landmarks)[keypoints_to_check]
            current_gesture[stage] = normalized_landmarks.tolist()
            status_label.config(text=f"{stage} frame recorded!", foreground="green")

def save_gesture():
    global current_gesture
    if len(current_gesture) < 4:
        status_label.config(text="Record all four keyframes (start, mid1, mid2, end)!", foreground="red")
        return
    
    gesture_name = simpledialog.askstring("Gesture Name", "Enter gesture name:")
    if gesture_name:
        gesture_dict[gesture_name] = current_gesture.copy()
        with open(GESTURE_FILE, "w") as f:
            json.dump(gesture_dict, f, indent=4)
        status_label.config(text=f"Gesture '{gesture_name}' saved successfully!", foreground="blue")
        current_gesture = {}

def update_webcam():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
        img = Image.fromarray(frame)
        img = img.resize((400, 300))
        imgtk = ImageTk.PhotoImage(image=img)
        webcam_label.imgtk = imgtk
        webcam_label.configure(image=imgtk)
    root.after(10, update_webcam)

def close_app():
    cap.release()
    cv2.destroyAllWindows()
    root.quit()

root = tk.Tk()
root.title("Gesture Capture UI")
root.geometry("500x600")

style = ttk.Style()
style.configure("TButton", padding=5, font=("Arial", 12))

webcam_label = ttk.Label(root)
webcam_label.pack()
update_webcam()

status_label = ttk.Label(root, text="Record gestures by clicking buttons", foreground="black")
status_label.pack(pady=10)

btn_start = ttk.Button(root, text="Record Start Frame", command=lambda: capture_frame("start"))
btn_start.pack(pady=5)

btn_mid1 = ttk.Button(root, text="Record Mid1 Frame", command=lambda: capture_frame("mid1"))
btn_mid1.pack(pady=5)

btn_mid2 = ttk.Button(root, text="Record Mid2 Frame", command=lambda: capture_frame("mid2"))
btn_mid2.pack(pady=5)

btn_end = ttk.Button(root, text="Record End Frame", command=lambda: capture_frame("end"))
btn_end.pack(pady=5)

btn_save = ttk.Button(root, text="Save Gesture", command=save_gesture)
btn_save.pack(pady=10)

btn_exit = ttk.Button(root, text="Exit", command=close_app)
btn_exit.pack(pady=10)

root.mainloop()
