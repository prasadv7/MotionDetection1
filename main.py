import cv2
import dlib
import numpy as np
import time
from PIL import ImageGrab
from pynput import mouse, keyboard
import threading
import win32gui
import os
import datetime
import sys

# Initialize the face detector, facial landmark predictor, and a Dlib model for gaze tracking
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("C:\\Users\\Prasad\\Desktop\\shape_predictor_68_face_landmarks.dat")
model = dlib.face_recognition_model_v1("C:\\Users\\Prasad\\Desktop\\dlib_face_recognition_resnet_model_v1.dat")

# Initialize variables for gaze tracking
looking_away = False
start_time = None

# Initialize variables for activity monitoring
keystroke_count = 0
mouse_movement_count = 0
activity_threshold = 10
browser_title = "Screen monitoring with Python. - Google Chrome"

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Path to save screenshots and video
screenshot_path = "C:\\Users\\Prasad\\Desktop\\StudentData\\"

# Prompt for student name
student_name = input("Enter the student's name: ")

# Create a folder for the student with timestamp if it doesn't exist
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
student_folder = os.path.join(screenshot_path, f"{student_name}_{timestamp}")
os.makedirs(student_folder, exist_ok=True)

# Define the video file name and codec
video_filename = os.path.join(student_folder, f"{student_name}_{timestamp}_video.avi")
fourcc = cv2.VideoWriter_fourcc(*'XVID')
w, h = int(cap.get(3)), int(cap.get(4))
video_writer = cv2.VideoWriter(video_filename, fourcc, 20.0, (w, h))

# Create a log file for the student
log_file_path = os.path.join(student_folder, f"{student_name}_{timestamp}_log.txt")

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
            event = f"Unusual application accessed: {active_window_title}"
            print(event)
            with open(log_file_path, "a") as log_file:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"{timestamp} - {event}\n")

        if active_window_title != browser_title:
            if keystroke_count > activity_threshold:
                event = "Unusual keyboard activity detected outside the browser."
                print(event)
                with open(log_file_path, "a") as log_file:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_file.write(f"{timestamp} - {event}\n")
                keystroke_count = 0
            if mouse_movement_count > activity_threshold:
                event = "Unusual mouse activity detected outside the browser."
                print(event)
                with open(log_file_path, "a") as log_file:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_file.write(f"{timestamp} - {event}\n")
                mouse_movement_count = 0

        time.sleep(1)  # Reduce the polling frequency

# Define a function to capture screenshots
def capture_screenshot():
    while True:
        active_window_title = get_active_window_title()
        if active_window_title != browser_title:
            print(f"Unusual application accessed: {active_window_title}")
            sanitized_title = "".join([c for c in active_window_title if c.isalnum() or c in (' ', '-', '_')])
            file_path = os.path.join(student_folder, f"{sanitized_title}.png")
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
        time.sleep(1)  # Reduce the polling frequency

# ... (The rest of your code for gaze tracking and webcam capture)
def get_active_window_title():
    active_window = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(active_window)
    return window_title
# Initialize the listener for mouse and keyboard events
keyboard_listener = keyboard.Listener(on_release=on_key_release)
mouse_listener = mouse.Listener(on_move=on_move)

# Initialize threads for browser activity and screenshot capture
activity_thread = threading.Thread(target=check_browser_activity)
screenshot_thread = threading.Thread(target=capture_screenshot)

# Start the activity and screenshot threads
activity_thread.daemon = True
screenshot_thread.daemon = True

keyboard_listener.start()
mouse_listener.start()
activity_thread.start()
screenshot_thread.start()

exit_flag = False  # Initialize the exit flag

# Register a listener for Ctrl+C or q to safely exit
def on_key_press(key):
    global exit_flag
    try:
        if key.char == 'q' and (key.ctrl or key.cmd):
            exit_flag = True
    except AttributeError:
        pass

# Initialize the listener for Ctrl+C or q
keyboard_listener_exit = keyboard.Listener(on_press=on_key_press)
keyboard_listener_exit.start()

while True:
    if exit_flag:
        # Safely exit the program
        break

    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if len(faces) == 0:
        if not looking_away:
            start_time = time.time()
            looking_away = True
            print("Looked away from the screen")
    else:
        landmarks = predictor(gray, faces[0])
        left_eye = np.array([(landmarks.part(36).x + landmarks.part(37).x) / 2, (landmarks.part(36).y + landmarks.part(37).y) / 2])
        right_eye = np.array([(landmarks.part(42).x + landmarks.part(43).x) / 2, (landmarks.part(42).y + landmarks.part(43).y) / 2])
        screen_center = np.array([frame.shape[1] // 2, frame.shape[0] // 2])
        eye_distance = np.linalg.norm(screen_center - ((left_eye + right_eye) / 2))

        if eye_distance > 50:
            if not looking_away:
                start_time = time.time()
                looking_away = True
                print("Looked away from the screen")
        else:
            if looking_away:
                end_time = time.time()
                if start_time is not None:
                    duration = end_time - start_time
                    if duration >= 3:
                        event = f"Looked away from the screen for {duration:.2f} seconds"
                        print(event)
                        looking_away = False
                        with open(log_file_path, "a") as log_file:
                            timestamp = datetime.datetime.now().strftime("%Y-%M-%d %H:%M:%S")
                            log_file.write(f"{timestamp} - {event}\n")

                        # Overlay the timestamp on the frame
                        frame = cv2.putText(frame, event, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                        # Add the frame to the video
                        video_writer.write(frame)

    cv2.imshow("Gaze Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit_flag = True

# Release the video writer
video_writer.release()

cap.release()
cv2.destroyAllWindows()
