import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import streamlit as st

MODEL_PATH = Path(__file__).resolve().parent / "yolov8plate.pt"

@st.cache_resource(show_spinner="Loading YOLOv8 Plate Detection Model...")
def load_detection_model():
    """Load and cache YOLO model."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    model = YOLO(str(MODEL_PATH))
    model.names[0] = "plate"
    return model

def detect_plate(image_path, conf_threshold=0.25, imgsz=1024):
    """
    Detect license plates using high-resolution inference and generous boundary padding.
    """
    model = load_detection_model()
    results = model(image_path, imgsz=imgsz, conf=conf_threshold, verbose=False)
    
    img = cv2.imread(image_path)
    if img is None:
        return [], [], None
    
    h, w = img.shape[:2]
    cropped_rois = []
    boxes = []
    annotated_img = img.copy()
    
    for r in results:
        for box in r.boxes:
            conf = float(box.conf[0])
            if conf < conf_threshold:
                continue
            
            coords = box.xyxy[0].cpu().numpy()
            x1 = max(0, int(coords[0]))
            y1 = max(0, int(coords[1]))
            x2 = min(w, int(coords[2]))
            y2 = min(h, int(coords[3]))
            
            if x2 > x1 and y2 > y1:
                # Add 10% padding around box to prevent cropping edge characters
                pad_x = int((x2 - x1) * 0.10)
                pad_y = int((y2 - y1) * 0.10)
                x1_pad = max(0, x1 - pad_x)
                y1_pad = max(0, y1 - pad_y)
                x2_pad = min(w, x2 + pad_x)
                y2_pad = min(h, y2 + pad_y)
                
                roi = img[y1_pad:y2_pad, x1_pad:x2_pad]
                cropped_rois.append(roi)
                boxes.append((x1, y1, x2, y2, conf))
                
                # Draw high-visibility bounding box
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 220, 0), 3)
                cv2.putText(
                    annotated_img,
                    f"Plate {conf*100:.0f}%",
                    (x1, max(25, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 220, 0),
                    2
                )
                
    return cropped_rois, boxes, annotated_img
