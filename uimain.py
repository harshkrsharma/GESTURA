import customtkinter as ctk
import subprocess

# Function to launch scripts
def run_script(script_name):
    try:
        subprocess.Popen(["python", script_name])
    except Exception as e:
        status_label.configure(text=f"Error: {e}", text_color="red")

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
    ("Settings", "orange", "settings.py"),
    ("Exit", "red", root.quit)
]

for text, color, script in buttons:
    btn = ctk.CTkButton(frame, text=text, fg_color=color, command=lambda s=script: run_script(s) if isinstance(s, str) else s())
    btn.pack(pady=5, padx=20, fill="x")

status_label = ctk.CTkLabel(frame, text="Select an option", text_color="white")
status_label.pack(pady=10)

root.mainloop()
