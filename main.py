import cv2
import numpy as np
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import supervision as sv

app = Flask(__name__)
CORS(app)  # Allow frontend access from React

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

box_annotator = sv.BoxAnnotator(
    thickness=2,
    text_thickness=2,
    text_scale=1
)

# Global variable to control the live stream
streaming = False

# Initialize Webcam (but don't start capturing yet)
cap = None

def generate_frames():
    global cap, streaming
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while streaming:
        success, frame = cap.read()
        if not success:
            break

        result = model(frame, agnostic_nms=True)[0]
        detections = sv.Detections.from_yolov8(result)
        object_count = len(detections)

        labels = [
            f"{model.names[int(class_id)]}, {confidence:.2f}"
            for _, confidence, class_id, _ in detections
        ]
        frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

        cv2.putText(frame, f"Objects: {object_count}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route("/video_feed")
def video_feed():
    global streaming
    streaming = True
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/stop_stream", methods=["POST"])
def stop_stream():
    global streaming, cap
    streaming = False
    if cap:
        cap.release()
    return jsonify({"message": "Stream stopped"}), 200

@app.route("/detect", methods=["POST"])
def detect_objects():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    image = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    result = model(image, agnostic_nms=True)[0]
    detections = sv.Detections.from_yolov8(result)

    labels = [
        f"{model.names[int(class_id)]}, {confidence:.2f}"
        for _, confidence, class_id, _ in detections
    ]
    image = box_annotator.annotate(scene=image, detections=detections, labels=labels)

    _, buffer = cv2.imencode(".jpg", image)
    return Response(buffer.tobytes(), mimetype="image/jpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
