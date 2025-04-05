import customtkinter as ctk
import subprocess
import pyautogui
import json
from tkinter import simpledialog, messagebox, filedialog
import os
from PIL import Image, ImageDraw

def create_placeholder_logo():
    if not os.path.exists("gestura_logo.png"):
        img = Image.new('RGB', (200, 200), 'white')
        draw = ImageDraw.Draw(img)
        # Draw a more stylized "G"
        draw.ellipse([20, 20, 180, 180], outline='black', width=8)  # Outer circle
        draw.arc([40, 40, 160, 160], start=0, end=180, fill='black', width=8)  # G curve
        draw.line([120, 100, 160, 100], fill='black', width=8)  # G line
        img.save("gestura_logo.png")

class HoverButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(corner_radius=15)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(scale_factor=1.05)

    def on_leave(self, event):
        self.configure(scale_factor=1.0)

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
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Gestura")
root.geometry("500x280")
root.resizable(False, False)  # Prevent resizing (width, height)

# Create main container with padding
main_frame = ctk.CTkFrame(root, fg_color="transparent")
main_frame.pack(pady=20, padx=30, fill="both", expand=True)

# Create two columns with specific weights
left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
right_frame.pack(side="right", fill="both", padx=(0, 0))

# Create and add logo
create_placeholder_logo()
try:
    logo_image = ctk.CTkImage(Image.open("gestura_logo.jpg"), size=(180, 180))
    logo_label = ctk.CTkLabel(left_frame, image=logo_image, text="")
    logo_label.pack()
    
    # Add stylish text below logo
    # app_name = ctk.CTkLabel(
    #     left_frame, 
    #     text="GESTURA",
    #     font=("Arial", 36, "bold"),
    #     text_color=("gray10", "gray90")
    # )
    # app_name.pack(pady=(0, 10))
    
    # app_desc = ctk.CTkLabel(
    #     left_frame, 
    #     text="Gesture Recognition System",
    #     font=("Arial", 14),
    #     text_color=("gray40", "gray60")
    # )
    # app_desc.pack()
    
except Exception as e:
    print(f"Error loading logo: {e}")
    logo_label = ctk.CTkLabel(left_frame, text="GESTURA", font=("Arial", 48, "bold"))
    logo_label.pack(pady=20)

# Create a frame for buttons to control their width
button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
button_frame.pack(fill="both", expand=True)

# Button configurations
button_configs = [
    {
        "text": "Record",
        "icon": "🎥",
        "color": "#2ecc71",
        "hover_color": "#27ae60",
        "script": "record_gestures.py"
    },
    {
        "text": "Action",
        "icon": "⚡",
        "color": "#3498db",
        "hover_color": "#2980b9",
        "script": "main.py"
    },
    {
        "text": "Launch Script",
        "icon": "🚀",
        "color": "#9b59b6",
        "hover_color": "#8e44ad",
        "script": add_custom_gesture
    }
]

# Calculate spacing
button_height = 45
total_buttons = len(button_configs)
available_height = 180  # Approximate height matching logo section
spacing = (available_height - (button_height * total_buttons)) // (total_buttons + 1)

# Add buttons with consistent spacing
for config in button_configs:
    btn = HoverButton(
        button_frame,
        text=f"{config['icon']} {config['text']}",
        fg_color=config['color'],
        hover_color=config['hover_color'],
        width=180,
        height=button_height,
        corner_radius=12,
        font=("Arial", 14),
        command=lambda s=config['script']: run_script(s) if isinstance(s, str) else s()
    )
    btn.pack(pady=spacing)

# Status label with modern styling
status_label = ctk.CTkLabel(
    main_frame, 
    text="", 
    text_color=("gray40", "gray60"),
    font=("Arial", 12)
)
status_label.pack(pady=10)

# Make the window responsive
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

root.mainloop()
