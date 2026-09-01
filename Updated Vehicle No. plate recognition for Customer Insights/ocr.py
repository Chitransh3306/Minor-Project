import easyocr
import re
import cv2
import numpy as np
import streamlit as st
from region_mapper import sanitize_and_score_plate

@st.cache_resource(show_spinner="Loading EasyOCR Engine...")
def load_ocr_reader():
    """Load and cache EasyOCR reader."""
    return easyocr.Reader(['en'], gpu=False)

def build_ensemble_variants(roi):
    """
    Generate multiple enhanced image variants for small/low-res plates:
    1. Unsharp Masking (Super-resolution + edge sharpening)
    2. CLAHE Adaptive Contrast
    3. Otsu Binarization
    4. Inverted Otsu Binarization (Handles dark text on light and light text on dark)
    5. Adaptive Gaussian Threshold
    """
    if roi is None or roi.size == 0:
        return []
    
    h, w = roi.shape[:2]
    # Upscale dynamically: ensure height is at least 110px
    scale = max(3.5, 110.0 / max(1, h))
    scaled = cv2.resize(roi, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)
    gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)
    
    # Laplacian / Unsharp sharpening
    gaussian = cv2.GaussianBlur(gray, (0, 0), 2.0)
    unsharp = cv2.addWeighted(gray, 2.2, gaussian, -1.2, 0)
    
    # Variant 1: CLAHE Contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(unsharp)
    
    # Variant 2: Otsu Binary
    _, otsu = cv2.threshold(cl, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Variant 3: Inverted Otsu Binary
    inv_otsu = cv2.bitwise_not(otsu)
    
    # Variant 4: Adaptive Gaussian Threshold
    adapt = cv2.adaptiveThreshold(cl, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 11)
    
    return [
        ("CLAHE", cl),
        ("Inverted Otsu", inv_otsu),
        ("Otsu", otsu),
        ("Adaptive", adapt),
        ("Raw ROI", roi)
    ]

def extract_plate_number(plate_images):
    """
    Extract license plate numbers using Multi-Pass Ensemble OCR with validation scoring.
    Returns: List of tuples (sanitized_plate, region_name, state_code)
    """
    reader = load_ocr_reader()
    results = []
    
    for roi in plate_images:
        if roi is None or roi.size == 0:
            continue
            
        variants = build_ensemble_variants(roi)
        best_plate = ""
        best_region = "Unknown Region"
        best_state = "XX"
        best_score = -999
        
        for name, img_var in variants:
            tokens = reader.readtext(img_var, detail=0)
            if not tokens:
                continue
            raw_text = " ".join(tokens)
            plate, region, state, score = sanitize_and_score_plate(raw_text)
            
            if score > best_score and plate:
                best_score = score
                best_plate = plate
                best_region = region
                best_state = state
                
        if best_plate:
            results.append((best_plate, best_region, best_state))
            
    return results
