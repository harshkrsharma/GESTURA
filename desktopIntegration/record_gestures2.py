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

cap = cv2.VideoCapture(0)
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

def capture_frame(stage, button):
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
            status_label.configure(text=f"{stage} captured!", text_color="#008000")
            # Update button color and text to show completion
            button.configure(fg_color="#90EE90", text=f"✓ {button.original_text}", 
                           text_color="#000000", hover_color="#98FB98")

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
        # Reset button colors and text
        for btn, _ in button_refs:
            if "Record" in btn.cget('text'):
                btn.configure(fg_color=btn.original_color, text=btn.original_text)

def update_webcam():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Get current frame size
        frame_height = max(webcam_frame.winfo_height(), 240)  # Minimum height of 240
        frame_width = max(webcam_frame.winfo_width(), 320)    # Minimum width of 320
        
        # Maintain aspect ratio
        aspect_ratio = 4/3
        if frame_width/frame_height > aspect_ratio:
            new_width = int(frame_height * aspect_ratio)
            new_height = frame_height
        else:
            new_width = frame_width
            new_height = int(frame_width / aspect_ratio)
            
        # Ensure minimum dimensions
        new_width = max(new_width, 320)
        new_height = max(new_height, 240)
            
        try:
            img = Image.fromarray(frame).resize((new_width, new_height))
            imgtk = ImageTk.PhotoImage(image=img)
            webcam_label.imgtk = imgtk
            webcam_label.configure(image=imgtk)
        except ValueError:
            # If resize fails, use minimum dimensions
            img = Image.fromarray(frame).resize((320, 240))
            imgtk = ImageTk.PhotoImage(image=img)
            webcam_label.imgtk = imgtk
            webcam_label.configure(image=imgtk)
            
    root.after(10, update_webcam)

def close_app():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

# Modern UI with customtkinter - Light theme with blue colors
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Gesture Capture UI")
root.geometry("500x280")  # Reduced window size
root.minsize(500, 280)    # Reduced minimum size
root.protocol("WM_DELETE_WINDOW", close_app)

# Configure the root background color - Light blue
root.configure(fg_color="#FFFFFF")

# Add power button in top right corner - Made smaller
power_button = ctk.CTkButton(
    root, 
    text="⏻", 
    width=25, 
    height=25,
    command=close_app,
    fg_color="#1E90FF",
    hover_color="#4169E1",
    text_color="white"
)
# power_button.place(relx=0.97, rely=0.02, anchor="ne")

# Main container frame using grid
main_frame = ctk.CTkFrame(root, fg_color="#E6F3FF")
main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # Reduced padding
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Configure main frame grid with adjusted weights
main_frame.grid_columnconfigure(0, weight=4)  # Increased webcam proportion
main_frame.grid_columnconfigure(1, weight=1)  # Reduced buttons proportion
main_frame.grid_rowconfigure(0, weight=1)

# Left frame for webcam using grid
left_frame = ctk.CTkFrame(main_frame, fg_color="#E6F3FF")
left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")  # Reduced padding

# Right frame for buttons using grid - Made narrower
right_frame = ctk.CTkFrame(main_frame, fg_color="#E6F3FF")
right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")  # Reduced padding

# Configure right frame grid
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_rowconfigure(0, weight=4)  # More space for grid
right_frame.grid_rowconfigure(1, weight=1)  # Save button
right_frame.grid_rowconfigure(2, weight=1)  # Exit button

# Webcam frame for proper scaling
webcam_frame = ctk.CTkFrame(left_frame, fg_color="#E6F3FF")
webcam_frame.pack(expand=True, fill="both", padx=10, pady=10)

# Webcam label
webcam_label = ctk.CTkLabel(webcam_frame, text="")
webcam_label.pack(expand=True, fill="both")
update_webcam()

status_label = ctk.CTkLabel(
    left_frame, 
    text="Record gestures using the buttons", 
    text_color="#000000",
    font=("Arial", 12, "bold")  # Reduced font size
)
status_label.pack(pady=5)  # Reduced padding

# Create grid frame for buttons
grid_frame = ctk.CTkFrame(right_frame, fg_color="#E6F3FF")
grid_frame.pack(side="top", fill="x", padx=10, pady=5)  # Changed to pack instead of grid

# Create 2x2 grid of buttons with fixed height
button_frame1 = ctk.CTkFrame(grid_frame, fg_color="#E6F3FF")
button_frame1.pack(side="top", fill="x", pady=2)
button_frame2 = ctk.CTkFrame(grid_frame, fg_color="#E6F3FF")
button_frame2.pack(side="top", fill="x", pady=2)

# Button configurations
button_configs = [
    ("Start", "#1E90FF", lambda btn=None: capture_frame("start", btn)),
    ("Mid 1", "#4169E1", lambda btn=None: capture_frame("mid1", btn)),
    ("Mid 2", "#0000CD", lambda btn=None: capture_frame("mid2", btn)),
    ("End", "#000080", lambda btn=None: capture_frame("end", btn))
]

button_refs = []

# First row of buttons
for i in range(2):
    text, color, command = button_configs[i]
    btn = ctk.CTkButton(
        button_frame1,
        text=text,
        fg_color=color,
        text_color="white",
        font=("Arial", 11, "bold"),
        width=100,
        height=30,     # Now this height setting will work
        hover_color="#4169E1",
        corner_radius=6
    )
    btn.original_color = color
    btn.original_text = text
    btn.hover_color = "#4169E1"
    btn.configure(command=lambda b=btn, cmd=command: cmd(b))
    btn.pack(side="left", expand=True, padx=2)
    button_refs.append((btn, color))

# Second row of buttons
for i in range(2, 4):
    text, color, command = button_configs[i]
    btn = ctk.CTkButton(
        button_frame2,
        text=text,
        fg_color=color,
        text_color="white",
        font=("Arial", 11, "bold"),
        width=100,
        height=30,     # Now this height setting will work
        hover_color="#4169E1",
        corner_radius=6
    )
    btn.original_color = color
    btn.original_text = text
    btn.hover_color = "#4169E1"
    btn.configure(command=lambda b=btn, cmd=command: cmd(b))
    btn.pack(side="left", expand=True, padx=2)
    button_refs.append((btn, color))

# Save button with increased width
save_btn = ctk.CTkButton(
    right_frame,
    text="Save",
    fg_color="#1E90FF",
    text_color="white",
    font=("Arial", 11, "bold"),
    width=200,      # Wide button
    height=30,
    hover_color="#4169E1",
    corner_radius=6,
    command=save_gesture
)
save_btn.pack(pady=2, padx=10)
button_refs.append((save_btn, "#1E90FF"))

# Exit button with same width as save button
btn_exit = ctk.CTkButton(
    right_frame,
    text="Exit",
    fg_color="#DC143C",    # Crimson red
    hover_color="#B22222",
    text_color="white",
    font=("Arial", 11, "bold"),
    width=200,      # Same width as save button
    height=30,
    corner_radius=6,
    command=close_app
)
btn_exit.pack(pady=2, padx=10)

root.mainloop()
