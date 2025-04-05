import pyautogui
import subprocess

GESTURE_ACTIONS = {
    "pause_video": lambda: pyautogui.press('space'),
    "volume_up": lambda: [pyautogui.press('volumeup') for _ in range(3)],
    "volume_down": lambda: [pyautogui.press('volumedown') for _ in range(3)],
    "mute": lambda: pyautogui.press('volumemute'),
    "seek_forward": lambda: pyautogui.hotkey('5'),
    "seek_backward": lambda: pyautogui.hotkey('left'),
    "brightness_up": lambda: pyautogui.press('brightnessup'),
    "brightness_down": lambda: pyautogui.press('brightnessdown'),

    "open_chrome": lambda: subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    "close": lambda: pyautogui.hotkey('alt', 'f4'),
    "close_window": lambda: pyautogui.hotkey('alt', 'f4'),
    "screenshot": lambda: pyautogui.hotkey('win', 'printscreen'),
    "go": lambda: subprocess.Popen(r'C:/Program Files/Mozilla Firefox/firefox.exe'),
    "good": lambda: subprocess.Popen(r'C:/Program Files/Mozilla Firefox/firefox.exe'),
}
