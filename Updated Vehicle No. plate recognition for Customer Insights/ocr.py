import easyocr

reader = easyocr.Reader(['en'])

def extract_plate_number(plate_images):
    plate_numbers = []
    for roi in plate_images:
        text = reader.readtext(roi, detail=0)
        number = ''.join(text).replace(" ", "")
        if number:
            plate_numbers.append(number)
    return plate_numbers
