import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
import time

try:
    # Initialize Firebase credentials
    cred = credentials.Certificate("C:\\Users\\Prasad\\Desktop\\motiondetection-371f1-firebase-adminsdk-5hgd8-1c10880242.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'motiondetection-371f1.appspot.com'  # Corrected Firebase Storage bucket name
    })

    # Initialize Firestore and Storage
    db = firestore.client()
    bucket = storage.bucket()  # Create a reference to the default storage bucket

    # Define a reference to the students collection
    students_ref = db.collection('students')

    # Function to upload a file to Firebase Cloud Storage and get its download URL
    def upload_file_to_storage(file_path, destination_blob_name):
        try:
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            # Set the file to be publicly accessible (adjust permissions as needed)
            blob.make_public()
            return blob.public_url
        except Exception as upload_error:
            print(f"Error uploading file to storage: {upload_error}")

    # Function to create a student record with uploaded files
    def create_student_record(student_name, screenshot_path, video_path, log_path):
        try:
            # Create a folder for the student using their name and timestamp
            folder_name = f"{student_name}_{int(time.time())}"  # Add a timestamp to make the folder name unique
            folder_path = f"students/{folder_name}/"

            # Upload files to the folder
            screenshot_url = upload_file_to_storage(screenshot_path, folder_path + "screenshot.jpg")
            video_url = upload_file_to_storage(video_path, folder_path + "video.mp4")
            log_url = upload_file_to_storage(log_path, folder_path + "log.txt")

            student_data = {
                'name': student_name,
                'folder_name': folder_name,
                'screenshot_url': screenshot_url,
                'video_url': video_url,
                'log_url': log_url,
                'timestamp': firestore.SERVER_TIMESTAMP
            }

            doc_ref = students_ref.add(student_data)
            return doc_ref[1].id  # Access the ID from the tuple
        except Exception as create_error:
            print(f"Error creating student record: {create_error}")

    # Function to retrieve student records
    def retrieve_student_records():
        try:
            students = students_ref.stream()
            for student in students:
                student_data = student.to_dict()
                if 'name' in student_data:
                    print(f"Student Name: {student_data['name']}")
                    if 'screenshot_url' in student_data:
                        print(f"Screenshot URL: {student_data['screenshot_url']}")
                    if 'video_url' in student_data:
                        print(f"Video URL: {student_data['video_url']}")
                    if 'log_url' in student_data:
                        print(f"Log URL: {student_data['log_url']}")
                else:
                    print("Student name not found in the document.")
        except Exception as retrieve_error:
            print(f"Error retrieving student records: {retrieve_error}")

    # Example of creating and retrieving student records
    student_name = input("Enter student name: ")
    screenshot_path = "C:\\Users\\Prasad\\Desktop\\StudentData\\ss.png"  # Replace with the actual file path on your system
    video_path = "C:\\Users\\Prasad\\Desktop\\StudentData\\vdo.avi"  # Replace with the actual file path on your system
    log_path = "C:\\Users\\Prasad\\Desktop\\StudentData\\log.txt"  # Replace with the actual file path on your system

    doc_id = create_student_record(student_name, screenshot_path, video_path, log_path)
    print(f"Created Student Record with ID: {doc_id}")

    print("Retrieving Student Records:")
    retrieve_student_records()
except Exception as main_error:
    print(f"Main error: {main_error}")
