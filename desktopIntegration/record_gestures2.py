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
button_texts = ["Start Frame", "Mid1 Frame", "Mid2 Frame", "End Frame"]
stages = ["start", "mid1", "mid2", "end"]

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
    
    gesture_name = name_entry.get()
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
                
        img = Image.fromarray(frame).resize((320, 240))
        imgtk = ImageTk.PhotoImage(image=img)
        webcam_label.imgtk = imgtk
        webcam_label.configure(image=imgtk)
    root.after(10, update_webcam)

def close_app():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

# UI Setup
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("Gesture Capture UI")
root.geometry("1000x700")  # Increased height for better vertical spacing
root.protocol("WM_DELETE_WINDOW", close_app)

frame = ctk.CTkFrame(root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# Camera Overlay
webcam_label = ctk.CTkLabel(frame,  width=480, height=380)
webcam_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
update_webcam()

# Gesture Capture Buttons - First Row
btn1 = ctk.CTkButton(frame, text=button_texts[0], command=lambda s=stages[0]: capture_frame(s), 
                   width=240, height=60, font=("Arial", 12))
btn1.grid(row=0, column=1, padx=3, pady=0)

btn2 = ctk.CTkButton(frame, text=button_texts[1], command=lambda s=stages[1]: capture_frame(s), 
                   width=240, height=60, font=("Arial", 12))
btn2.grid(row=0, column=2, padx=3, pady=0)

# Name Entry and Save Button
name_entry = ctk.CTkEntry(frame, placeholder_text="Gesture Name", width=240, height=40, font=("Arial", 12))
name_entry.grid(row=1, column=1, pady=5, padx=3, sticky="ew")

save_btn = ctk.CTkButton(frame, text="Save Gesture", command=save_gesture, 
                        width=240, height=40, font=("Arial", 12))
save_btn.grid(row=1, column=2, pady=5, padx=3, sticky="ew")

# Gesture Capture Buttons - Second Row
btn3 = ctk.CTkButton(frame, text=button_texts[2], command=lambda s=stages[2]: capture_frame(s), 
                   width=240, height=60, font=("Arial", 12))
btn3.grid(row=2, column=1, padx=3, pady=0)

btn4 = ctk.CTkButton(frame, text=button_texts[3], command=lambda s=stages[3]: capture_frame(s), 
                   width=240, height=60, font=("Arial", 12))
btn4.grid(row=2, column=2, padx=3, pady=0)

status_label = ctk.CTkLabel(frame, text="Record gestures using buttons", 
                           text_color="black", font=("Arial", 12))
status_label.grid(row=3, column=0, columnspan=4, pady=5)

root.mainloop()