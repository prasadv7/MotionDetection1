import cv2
import dlib
import time
import numpy as np
import pyaudio
import threading
from tkinter import messagebox

# Initialize the face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("C:\\Users\\Prasad\\Desktop\\shape_predictor_68_face_landmarks.dat")  # Download this file

# Initialize variables for gaze tracking
looking_away = False
start_time = None
popup_shown = False  # Initialize a flag to track whether the popup message has been shown

# Initialize variables for sound monitoring
sound_threshold = 0.1  # Adjust this threshold as needed
audio_buffer = []
audio_lock = threading.Lock()

# Function to detect gaze and show popup
# ... (previous code)

# Function to detect gaze and show popup
def detect_gaze(gray, frame):
    def detect_gaze(gray, frame):
        global looking_away, start_time, popup_shown

        faces = detector(gray)
        for face in faces:
            landmarks = predictor(gray, face)

            # Calculate the distance between the center of the eyes
            left_eye_center = np.mean([landmarks.part(36), landmarks.part(37)], axis=0)
            right_eye_center = np.mean([landmarks.part(42), landmarks.part(43)], axis=0)
            eye_distance = np.linalg.norm(left_eye_center - right_eye_center)

            print("Eye Distance:", eye_distance)  # Add this line for debugging

            # Check if the user is looking away (adjust the threshold as needed)
            if eye_distance > 50:  # Adjust this threshold as needed
                if not looking_away:
                    start_time = time.time()
                    looking_away = True
                    if not popup_shown:
                        show_message("Look back at the screen!")
                        popup_shown = True
            else:
                if looking_away:
                    end_time = time.time()
                    if start_time is not None:  # Check if start_time is set
                        duration = end_time - start_time
                        print("Duration:", duration)  # Add this line for debugging
                        if duration >= 3.0:
                            looking_away = False

        cv2.imshow("Proctoring", frame)


# ... (rest of the code)


# Function to calculate the eye aspect ratio (EAR)
def eye_aspect_ratio(eye):
    a = np.linalg.norm(eye[1] - eye[5])
    b = np.linalg.norm(eye[2] - eye[4])
    c = np.linalg.norm(eye[0] - eye[3])
    return (a + b) / (2.0 * c)

# Function to display a message box
def show_message(message):
    global paused
    result = messagebox.askquestion("Paused", message + "\nDo you want to resume the exam?")
    if result == "yes":
        paused = False
    else:
        paused = True

# Function to monitor audio
def monitor_audio():
    global audio_buffer

    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    while True:
        data = stream.read(1024)
        audio_data = np.frombuffer(data, dtype=np.int16)
        if np.max(np.abs(audio_data)) > sound_threshold * np.iinfo(np.int16).max:
            audio_lock.acquire()
            audio_buffer.append(time.time())
            audio_lock.release()

# Function to check for suspicious audio activity
def check_audio():
    global looking_away, popup_shown

    while True:
        if len(audio_buffer) > 0:
            audio_lock.acquire()
            last_audio_time = audio_buffer[-1]
            audio_lock.release()
            current_time = time.time()
            if current_time - last_audio_time >= 3.0:
                if not looking_away and not popup_shown:
                    show_message("Possible cheating (sound detected)!")
                    popup_shown = True
                looking_away = True

# Start audio monitoring thread
audio_thread = threading.Thread(target=monitor_audio)
audio_thread.daemon = True
audio_thread.start()

# Start audio checking thread
audio_check_thread = threading.Thread(target=check_audio)
audio_check_thread.daemon = True
audio_check_thread.start()

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Initialize variables for pausing the exam
paused = False

# Function to check if the user has been looking away for 3 seconds
def check_gaze():
    global looking_away, start_time, paused
    while True:
        if not paused and looking_away:
            end_time = time.time()
            if start_time is not None:  # Check if start_time is set
                duration = end_time - start_time
                if duration >= 3:
                    looking_away = False
        time.sleep(1)

# Start the gaze checking thread
gaze_thread = threading.Thread(target=check_gaze)
gaze_thread.daemon = True
gaze_thread.start()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        # Get the coordinates of the eyes
        left_eye = landmarks.part(36)
        right_eye = landmarks.part(45)

        # Calculate the distance between the eyes
        eye_distance = abs(right_eye.x - left_eye.x)

        # If the distance is greater than a threshold, consider the user as looking away
        if eye_distance > 50:  # Adjust this threshold as needed
            if not looking_away:
                start_time = time.time()
                looking_away = True
        else:
            if looking_away:
                end_time = time.time()
                if start_time is not None:  # Check if start_time is set
                    duration = end_time - start_time
                    if duration >= 3 and not paused:  # Check if user has been looking away for 3 seconds
                        looking_away = False

    if not paused:
        cv2.imshow("Screen Watcher", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
