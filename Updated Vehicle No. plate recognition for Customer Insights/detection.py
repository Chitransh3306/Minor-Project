from ultralytics import YOLO
import cv2

model = YOLO("yolov8plate.pt")

model.names[0] = "plate"

def detect_plate(image_path):
    results = model(image_path)
    detections = results[0].boxes.data
    img = cv2.imread(image_path)
    cropped_images = []

    for box in detections:
        x1, y1, x2, y2, conf, cls = map(int, box[:6])
        roi = img[y1:y2, x1:x2]
        cropped_images.append(roi)

    return cropped_images
