from detection import detect_plate
from ocr import extract_plate_number
from region_mapper import get_state_name
from database.db_handler import insert_vehicle

def process_vehicle(image_path):
    cropped = detect_plate(image_path)
    plates = extract_plate_number(cropped)
    results = []
    for plate in plates:
        state_name, code = get_state_name(plate)
        insert_vehicle(plate, code, state_name)
        results.append((plate, state_name))
    return results
