from pynput import mouse, keyboard
import threading
import time
import ctypes
import win32gui
from PIL import ImageGrab

keystroke_count = 0
mouse_movement_count = 0
activity_threshold = 10
browser_title = "Screen monitoring with Python. - Google Chrome"  # Modify this to match your browser's title


def on_key_release(key):
    global keystroke_count
    keystroke_count += 1


def on_move(x, y):
    global mouse_movement_count
    mouse_movement_count += 1


def check_browser_activity():
    global keystroke_count, mouse_movement_count
    while True:

        active_window_title = get_active_window_title()
        if active_window_title != browser_title:
            print(f"Unusual application accessed: {active_window_title}")

        if active_window_title != browser_title:

            if keystroke_count > activity_threshold:
                print("Unusual keyboard activity detected outside the browser.")

                keystroke_count = 0
            if mouse_movement_count > activity_threshold:
                print("Unusual mouse activity detected outside the browser.")

                mouse_movement_count = 0

        time.sleep(1)


def capture_screenshot():
    while True:
        active_window_title = get_active_window_title()
        if active_window_title != browser_title:
            print(f"Unusual application accessed: {active_window_title}")

            # Clean the window title for file naming (replace invalid characters)
            sanitized_title = "".join([c for c in active_window_title if c.isalnum() or c in (' ', '-', '_')])

            # Define the full file path
            file_path = f"C:\\Users\\Prasad\\Desktop\\StudentData\\{sanitized_title}.png"

            # Capture and save the screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)

        time.sleep(1)


def get_active_window_title():
    active_window = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(active_window)
    return window_title


keyboard_listener = keyboard.Listener(on_release=on_key_release)
mouse_listener = mouse.Listener(on_move=on_move)

keyboard_thread = threading.Thread(target=keyboard_listener.start)
mouse_thread = threading.Thread(target=mouse_listener.start)
activity_thread = threading.Thread(target=check_browser_activity)
screenshot_thread = threading.Thread(target=capture_screenshot)  # Add screenshot thread

keyboard_thread.daemon = True
mouse_thread.daemon = True
activity_thread.daemon = True
screenshot_thread.daemon = True  # Set screenshot thread as daemon

keyboard_thread.start()
mouse_thread.start()
activity_thread.start()
screenshot_thread.start()  # Start screenshot thread

# Continue with your exam proctoring code or other functionality here
