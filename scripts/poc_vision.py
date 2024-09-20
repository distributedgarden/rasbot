import os
import subprocess
import cv2
import mediapipe as mp
import urllib.request
from flask import Flask, Response, jsonify

app = Flask(__name__)

# Paths for Haar Cascade files and captured image
face_cascade_path = "haarcascade_frontalface_default.xml"
hand_cascade_path = "hand.xml"
image_path = "/tmp/latest_frame.jpg"

# MediaPipe hand detection setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


@app.route("/download_files")
def download_files():
    """
    Description:
        - Requirements for OpenCV
        - Download the required Haar Cascade XML files for face and hand detection.
    """
    face_url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    hand_url = (
        "https://github.com/Aravindlivewire/Opencv/raw/master/haarcascade/palm.xml"
    )

    urllib.request.urlretrieve(face_url, face_cascade_path)
    urllib.request.urlretrieve(hand_url, hand_cascade_path)

    return jsonify({"message": "Haar cascades downloaded successfully!"})


def capture_image():
    """
    Description:
        - Capture a single image using libcamera-still and save it to /tmp/latest_frame.jpg.
    """
    command = [
        "libcamera-still",
        "-o",
        image_path,
        "--width",
        "640",
        "--height",
        "480",
        "--nopreview",
    ]
    subprocess.run(command)


def detect_objects(img):
    """
    Description:
        - Detect faces and hands using Haar cascades and draw rectangles around them.
    """
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    hand_cascade = cv2.CascadeClassifier(hand_cascade_path)

    # Detection
    faces = face_cascade.detectMultiScale(
        gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    hands = hand_cascade.detectMultiScale(
        gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
    )

    # Draw rectangles
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    for x, y, w, h in hands:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return img


@app.route("/capture_haar")
def capture_haar():
    """
    Description:
        - Capture an image, perform face and hand detection using Haar Cascades, and return the processed image.
    """
    capture_image()

    img = cv2.imread(image_path)
    if img is None:
        return "Failed to capture image", 500

    # Detect objects (faces and hands) in the image
    img_with_detections = detect_objects(img)

    # Encode the processed image to JPEG
    ret, jpeg = cv2.imencode(".jpg", img_with_detections)
    if not ret:
        return "Failed to encode image", 500

    return Response(jpeg.tobytes(), mimetype="image/jpeg")


@app.route("/capture_mediapipe")
def capture_mediapipe():
    """
    Description:
        - Capture an image, perform hand detection using MediaPipe, and return the processed image.
    """
    capture_image()

    img = cv2.imread(image_path)
    if img is None:
        return "Failed to capture image", 500

    # Convert the image to RGB (MediaPipe works with RGB images)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Initialize MediaPipe hands model
    with mp_hands.Hands(
        static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5
    ) as hands:
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on the image
                mp_drawing.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

    # Encode the processed image to JPEG
    ret, jpeg = cv2.imencode(".jpg", img)
    if not ret:
        return "Failed to encode image", 500

    return Response(jpeg.tobytes(), mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
