import customtkinter as ctk
import subprocess
import pyautogui
import json
from tkinter import simpledialog, messagebox, filedialog
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

# Function to launch scripts
def run_script(script_name):
    try:
        subprocess.Popen(["python", script_name])
    except Exception as e:
        status_label.configure(text=f"Error: {e}", text_color="red")

# Function to add a custom gesture action
from tkinter import filedialog
import ast

def add_custom_gesture():
    gesture_name = simpledialog.askstring("Custom Gesture", "Enter Gesture Name:")
    if not gesture_name:
        return

    action_type = simpledialog.askstring("Action Type", "Type 'key' to map a keyboard key or 'app' to open an application:")
    if action_type not in ["key", "app"]:
        messagebox.showerror("Error", "Invalid action type. Use 'key' or 'app'.")
        return

    if action_type == "key":
        key = simpledialog.askstring("Key Mapping", "Enter the keyboard key to map:")
        if not key:
            return
        action_code = f"lambda: pyautogui.press('{key}')"
    else:
        app_path = filedialog.askopenfilename(title="Select Application", filetypes=[("Executable Files", "*.exe;*.bat;*.cmd"), ("All Files", "*.*")])
        if not app_path:
            return
        action_code = f"lambda: subprocess.Popen(r'{app_path}')"

    # Path to gesture_actions.py
    file_path = "gesture_actions.py"

    # Read existing content
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            lines = file.readlines()
    else:
        lines = ["import pyautogui\n", "import subprocess\n", "\n", "GESTURE_ACTIONS = {\n"]

    # Check if the gesture already exists
    for line in lines:
        if f'"{gesture_name}":' in line:
            messagebox.showerror("Error", f"Gesture '{gesture_name}' already exists.")
            return

    # Insert new gesture before the closing bracket
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "}":
            lines.insert(i, f'    "{gesture_name}": {action_code},\n')
            break
    else:
        # If "}" is not found, assume the dictionary is empty or malformed
        lines.append(f'    "{gesture_name}": {action_code},\n')
        lines.append("}\n")

    # Write back updated content
    with open(file_path, "w") as file:
        file.writelines(lines)

    messagebox.showinfo("Success", f"Gesture '{gesture_name}' saved successfully!")

# Initialize Modern UI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("ISL Recognition System")
root.geometry("500x400")

frame = ctk.CTkFrame(root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

ctk.CTkLabel(frame, text="Indian Sign Language System", font=("Arial", 20)).pack(pady=10)

# Buttons for menu options
buttons = [
    ("Record Gestures", "green", "record_gestures.py"),
    ("Run Main ISL Recognition", "blue", "main.py"),
    ("Custom Gesture Action", "purple", add_custom_gesture),
    ("Settings", "orange", "settings.py"),
    ("Exit", "red", root.quit)
]

for text, color, script in buttons:
    btn = ctk.CTkButton(frame, text=text, fg_color=color, command=lambda s=script: run_script(s) if isinstance(s, str) else s())
    btn.pack(pady=5, padx=20, fill="x")

status_label = ctk.CTkLabel(frame, text="Select an option", text_color="white")
status_label.pack(pady=10)

root.mainloop()
