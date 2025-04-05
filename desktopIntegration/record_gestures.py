import cv2
import json
import os
import numpy as np
import mediapipe as mp
import customtkinter as ctk
from tkinter import simpledialog
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
            status_label.configure(text=f"{stage} frame recorded!", text_color="green")

def save_gesture():
    global current_gesture
    if len(current_gesture) < 4:
        status_label.configure(text="Record all four keyframes!", text_color="red")
        return
    
    gesture_name = simpledialog.askstring("Gesture Name", "Enter gesture name:")
    if gesture_name:
        gesture_dict[gesture_name] = current_gesture.copy()
        with open(GESTURE_FILE, "w") as f:
            json.dump(gesture_dict, f, indent=4)
        status_label.configure(text=f"Gesture '{gesture_name}' saved!", text_color="blue")
        current_gesture = {}

def update_webcam():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
        img = Image.fromarray(frame).resize((400, 300))
        imgtk = ImageTk.PhotoImage(image=img)
        webcam_label.imgtk = imgtk
        webcam_label.configure(image=imgtk)
    root.after(10, update_webcam)

def close_app():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

# Modern UI with customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Gesture Capture UI")
root.geometry("550x650")
root.protocol("WM_DELETE_WINDOW", close_app)

frame = ctk.CTkFrame(root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

webcam_label = ctk.CTkLabel(frame, text="", width=400, height=300)
webcam_label.pack(pady=10)
update_webcam()

status_label = ctk.CTkLabel(frame, text="Record gestures using the buttons", text_color="white")
status_label.pack(pady=10)

buttons = [
    ("Record Start Frame", "green", lambda: capture_frame("start")),
    ("Record Mid1 Frame", "orange", lambda: capture_frame("mid1")),
    ("Record Mid2 Frame", "purple", lambda: capture_frame("mid2")),
    ("Record End Frame", "red", lambda: capture_frame("end")),
    ("Save Gesture", "blue", save_gesture)
]

for text, color, command in buttons:
    btn = ctk.CTkButton(frame, text=text, fg_color=color, command=command)
    btn.pack(pady=5, padx=20, fill="x")

btn_exit = ctk.CTkButton(frame, text="Exit", fg_color="gray", command=close_app)
btn_exit.pack(pady=10, padx=20, fill="x")

root.mainloop()
