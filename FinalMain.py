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
from plyer import notification
from firebase_admin import storage, credentials, initialize_app, firestore

# Initialize the face detector, facial landmark predictor, and a Dlib model for gaze tracking
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("C:\\Users\\Prasad\\Desktop\\shape_predictor_68_face_landmarks.dat")
model = dlib.face_recognition_model_v1("C:\\Users\\Prasad\\Desktop\\dlib_face_recognition_resnet_model_v1.dat")
cred = credentials.Certificate("C:\\Users\\Prasad\\Desktop\\motiondetection-371f1-firebase-adminsdk-5hgd8-1c10880242.json")

# Initialize the Firebase app with your credentials and specify the storage bucket
initialize_app(cred, {'storageBucket': 'motiondetection-371f1.appspot.com'})

# Initialize variables for gaze tracking
looking_away = False
start_time = None
db = firestore.client()

# Initialize variables for activity monitoring
keystroke_count = 0
mouse_movement_count = 0
activity_threshold = 10
browser_title = "Screen monitoring with Python. - Google Chrome"

# Initialize the webcam
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define the size of the video feed window
video_feed_width = 320
video_feed_height = 240

# Path to save screenshots and video
screenshot_path = "C:\\Users\\Prasad\\Desktop\\StudentData\\"

# Prompt for student name
student_name = input("Enter Your Name: ")
student_email = input("Enter the Email: ")

# Create a folder for the student with timestamp if it doesn't exist
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
student_folder = os.path.join(screenshot_path, f"{student_name}_{timestamp}")
os.makedirs(student_folder, exist_ok=True)

cv2.namedWindow("Video Feed", cv2.WINDOW_NORMAL)
cv2.moveWindow("Video Feed", frame_width - video_feed_width, frame_height - video_feed_height)

# Define the video file name and codec
video_filename = os.path.join(student_folder, f"{student_name}_{timestamp}_video.mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(video_filename, fourcc, 20.0, (frame_width, frame_height))

# Create a log file for the student
log_file_path = os.path.join(student_folder, f"{student_name}_{timestamp}_log.txt")


def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_icon=None,  # e.g., 'C:\\icon_32x32.ico'
        timeout=10,  # seconds
    )


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
            show_notification("Unusual application accessed", "Please Go back on your exam page")
            with open(log_file_path, "a") as log_file:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"{timestamp} - {event}\n")

        if active_window_title != browser_title:
            if keystroke_count > activity_threshold:
                event = "Unusual keyboard activity detected outside the browser."
                print(event)
                show_notification("Unusual keyboard activity detected outside the browser",
                                  "Please Go back on your exam page")

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
            show_notification("Unusual application accessed",
                              "Please Go back on your exam page")

            sanitized_title = "".join([c for c in active_window_title if c.isalnum() or c in (' ', '-', '_')])
            file_path = os.path.join(student_folder, f"{sanitized_title}.png")
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
        time.sleep(1)  # Reduce the polling frequency


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


def upload_files_to_firebase(local_path, bucket, student_name):
    start_time = time.time()
    file_count = 0

    # Create a folder based on the student's name in Firebase Storage if it doesn't exist
    student_ref = bucket.get_blob(student_name)
    if student_ref is None:
        student_ref = bucket.blob(student_name)
        student_ref.upload_from_string('')  # Create an empty file to represent the folder

    for root, dirs, files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            firebase_path = os.path.relpath(local_file_path, local_path)
            blob = bucket.blob(f"students/{student_name}/{firebase_path}")
            blob.upload_from_filename(local_file_path)
            blob.make_public()
            file_count += 1
            print(f"Uploaded {local_file_path} to {blob.path}")

    end_time = time.time()
    upload_time = end_time - start_time
    print(f"Uploaded {file_count} files in {upload_time:.2f} seconds.")


def create_student_record(student_name, student_folder):
    student_data = {
        'name': student_name,
        'folder_name': student_folder,
        'screenshot_urls': [],
        'video_url': '',
        'log_url': '',
        'timestamp': firestore.SERVER_TIMESTAMP
    }

    # Access Firebase Storage to get the URLs of files for the particular student
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix=f"students/{student_name}/")
    for blob in blobs:
        if blob.name.endswith('.png'):
            student_data['screenshot_urls'].append(blob.public_url)
        elif blob.name.endswith('.mp4'):
            student_data['video_url'] = blob.public_url
        elif blob.name.endswith('_log.txt'):
            student_data['log_url'] = blob.public_url

    # Create the Firestore record for the student
    students_ref = db.collection('students')
    students_ref.add(student_data)


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
        left_eye = np.array(
            [(landmarks.part(36).x + landmarks.part(37).x) / 2, (landmarks.part(36).y + landmarks.part(37).y) / 2])
        right_eye = np.array(
            [(landmarks.part(42).x + landmarks.part(43).x) / 2, (landmarks.part(42).y + landmarks.part(43).y) / 2])
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
                        show_notification("You Looked away", "")
                        looking_away = False
                        with open(log_file_path, "a") as log_file:
                            timestamp = datetime.datetime.now().strftime("%Y-%M-%d %H:%M:%S")
                            log_file.write(f"{timestamp} - {event}\n")

                        # Overlay the timestamp on the frame
                        frame = cv2.putText(frame, event, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the video feed in the window
    cv2.imshow("Video Feed", frame)

    # Write the video frame to the output video file
    video_writer.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit_flag = True

# Release the video writer
video_writer.release()

# Wait for threads to finish
# activity_thread.join()
# screenshot_thread.join()

# Add a delay before exiting to allow threads to finish
time.sleep(2)

cap.release()
cv2.destroyAllWindows()

# After releasing the video and saving it, upload data to Firebase
local_folder_path = student_folder

bucket = storage.bucket()
upload_files_to_firebase(local_folder_path, bucket, student_name)
create_student_record(student_name, student_folder)
