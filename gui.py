import cv2
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder

# Path to the pre-trained model and label map
MODEL_NAME = 'ssd_mobilenet_v2_coco'
PATH_TO_MODEL_DIR = "path/to/" + MODEL_NAME
PATH_TO_SAVED_MODEL = PATH_TO_MODEL_DIR + "/saved_model"

# Load the label map
PATH_TO_LABELS = "path/to/mscoco_label_map.pbtxt"
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

# Load the saved model
print('Loading model...', end='')
detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
print('Done!')

# Open a video capture object (0 for the default camera, or provide the path to a video file)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize the frame if needed
    # frame = cv2.resize(frame, (width, height))

    # Perform object detection
    image_np = np.array(frame)
    input_tensor = tf.convert_to_tensor([image_np])
    detections = detect_fn(input_tensor)

    # Visualization of the results
    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np,
        detections['detection_boxes'][0].numpy(),
        detections['detection_classes'][0].numpy().astype(int),
        detections['detection_scores'][0].numpy(),
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=.30,
        agnostic_mode=False
    )

    # Display the result
    cv2.imshow('Object Detection', cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture object and close the window
cap.release()
cv2.destroyAllWindows()
