import os
from firebase_admin import storage, credentials, initialize_app
import time

# Path to the folder you want to upload
local_folder_path = "C:\\Users\\Prasad\\Desktop\\StudentData\\Prasad Final_20231106195713"

# Your Firebase Admin SDK credentials file path
cred = credentials.Certificate("C:\\Users\\Prasad\\Desktop\\motiondetection-371f1-firebase-adminsdk-5hgd8-1c10880242.json")

# Initialize the Firebase app with your credentials and specify the storage bucket
initialize_app(cred, {'storageBucket': 'motiondetection-371f1.appspot.com'})

def upload_files_to_firebase(local_path, bucket):
    start_time = time.time()
    file_count = 0

    for root, dirs, files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            firebase_path = os.path.relpath(local_file_path, local_path)
            blob = bucket.blob(firebase_path)
            blob.upload_from_filename(local_file_path)
            file_count += 1
            print(f"Uploaded {local_file_path} to {blob.path}")

    end_time = time.time()
    upload_time = end_time - start_time
    print(f"Uploaded {file_count} files in {upload_time:.2f} seconds.")

if __name__ == "__main__":
    bucket = storage.bucket()
    upload_files_to_firebase(local_folder_path, bucket)
