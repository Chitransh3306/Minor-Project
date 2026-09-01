from detection import detect_plate
from ocr import extract_plate_number
from database.db_handler import insert_vehicle

def process_vehicle(image_path, conf_threshold=0.25):
    """
    Full pipeline: Plate Detection -> OCR -> Region Mapping -> DB Recording.
    Returns:
        results: List of dicts containing plate details
        annotated_image: Image with bounding box annotations
    """
    cropped_rois, boxes, annotated_img = detect_plate(image_path, conf_threshold=conf_threshold)
    if not cropped_rois:
        return [], annotated_img
    
    extracted_data = extract_plate_number(cropped_rois)
    results = []
    
    for i, (plate, state_name, state_code) in enumerate(extracted_data):
        conf = boxes[i][4] if i < len(boxes) else 1.0
        roi = cropped_rois[i] if i < len(cropped_rois) else None
        
        # Save record in DB
        insert_vehicle(plate, state_code, state_name, conf)
        
        results.append({
            "plate": plate,
            "state_code": state_code,
            "state_name": state_name,
            "confidence": conf,
            "roi": roi
        })
        
    return results, annotated_img
