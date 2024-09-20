import subprocess
import cv2
import numpy as np
from flask import Flask, Response
import mediapipe as mp

app = Flask(__name__)

# MediaPipe Hand Detection setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# FFmpeg and libcamera commands for video capture
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_CHANNELS = 3
FRAME_SIZE = FRAME_WIDTH * FRAME_HEIGHT * FRAME_CHANNELS
FFMPEG_CMD = [
    'ffmpeg', '-i', 'pipe:0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'
]
LIBCAMERA_CMD = [
    'libcamera-vid', '-t', '0', '--inline', '--width', str(FRAME_WIDTH),
    '--height', str(FRAME_HEIGHT), '--framerate', '5', '-o', '-'
]

def generate_frames():
    """
    Generator function that continuously captures video frames, performs hand detection using MediaPipe,
    and yields the frames as an MJPEG stream.

    Yields:
        - bytes: The MJPEG stream of video frames with hand landmarks.
    """
    libcamera_process = subprocess.Popen(LIBCAMERA_CMD, stdout=subprocess.PIPE, bufsize=10**8)
    ffmpeg_process = subprocess.Popen(FFMPEG_CMD, stdin=libcamera_process.stdout, stdout=subprocess.PIPE, bufsize=10**8)

    try:
        while True:
            # Read a frame from the video stream
            frame_bytes = ffmpeg_process.stdout.read(FRAME_SIZE)
            if len(frame_bytes) != FRAME_SIZE:
                print("Error: Incomplete frame")
                break

            # Convert the frame bytes to a NumPy array and reshape it
            frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape((FRAME_HEIGHT, FRAME_WIDTH, FRAME_CHANNELS))
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to BGR for OpenCV

            # Convert frame to RGB for MediaPipe processing
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

            # Perform hand detection using MediaPipe
            with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
                results = hands.process(frame_rgb)

                # Draw hand landmarks on the frame
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(frame_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Encode the frame as JPEG
            ret, jpeg = cv2.imencode('.jpg', frame_bgr)
            if not ret:
                print("Error: Failed to encode frame")
                break

            # Yield the frame as part of the MJPEG stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    finally:
        ffmpeg_process.terminate()
        libcamera_process.terminate()

@app.route('/detection-stream')
def hand_detection_stream():
    """
    Stream video with hand and finger detection using MediaPipe.

    Returns:
        - Response: The MJPEG stream of video frames with hand landmarks.
    """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
