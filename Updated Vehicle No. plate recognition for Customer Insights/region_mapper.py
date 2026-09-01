import re

STATE_MAP = {
    "AN": "Andaman & Nicobar Islands", "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh",
    "AS": "Assam", "BR": "Bihar", "CH": "Chandigarh", "CG": "Chhattisgarh",
    "DD": "Daman & Diu", "DN": "Dadra & Nagar Haveli", "DL": "Delhi", "GA": "Goa",
    "GJ": "Gujarat", "HR": "Haryana", "HP": "Himachal Pradesh", "JH": "Jharkhand",
    "JK": "Jammu & Kashmir", "KA": "Karnataka", "KL": "Kerala", "LA": "Ladakh",
    "LD": "Lakshadweep", "MP": "Madhya Pradesh", "MH": "Maharashtra", "MN": "Manipur",
    "ML": "Meghalaya", "MZ": "Mizoram", "NL": "Nagaland", "OD": "Odisha",
    "PB": "Punjab", "PY": "Puducherry", "RJ": "Rajasthan", "SK": "Sikkim",
    "TN": "Tamil Nadu", "TS": "Telangana", "TR": "Tripura", "UK": "Uttarakhand",
    "UA": "Uttarakhand", "UP": "Uttar Pradesh", "WB": "West Bengal", "BH": "Bharat Series"
}

STATE_CODES = set(STATE_MAP.keys())

CHAR_TO_NUM = {'O': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8', 'G': '6', 'Q': '0', 'D': '0'}
NUM_TO_CHAR = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B', '6': 'G', '4': 'A'}

def sanitize_and_score_plate(raw_text):
    """
    Cleans, validates, position-corrects, and scores an Indian license plate string.
    Returns: (cleaned_plate, region_name, state_code, validation_score)
    """
    if not raw_text:
        return "", "Unknown Region", "XX", -100
        
    text = raw_text.upper()
    cleaned = re.sub(r'[^A-Z0-9]', '', text)
    
    # Strip leading country tags
    if cleaned.startswith("IND") and len(cleaned) > 5:
        cleaned = cleaned[3:]
    elif cleaned.startswith("IN") and len(cleaned) > 6 and cleaned[2:4] in STATE_CODES:
        cleaned = cleaned[2:]
        
    best_candidate = None
    best_state = None
    
    # Search for known 2-letter state code
    for i in range(len(cleaned) - 1):
        two_chars = cleaned[i:i+2]
        if two_chars in STATE_CODES:
            candidate = cleaned[i:]
            if len(candidate) >= 4:
                best_candidate = candidate
                best_state = two_chars
                break
                
    if not best_candidate:
        # Fallback to standard regex
        m = re.search(r'([A-Z]{2})([0-9]{1,2})([A-Z]{0,3})([0-9]{1,4})', cleaned)
        if m:
            best_candidate = "".join(m.groups())
            best_state = m.group(1)
        else:
            best_candidate = cleaned
            best_state = cleaned[:2] if len(cleaned) >= 2 else "XX"

    plate = best_candidate
    score = 0
    
    if best_state in STATE_CODES:
        score += 50
    else:
        score -= 20
        
    # Positional character type correction for standard Indian plates (e.g. RJ 45 CJ 6865)
    if len(plate) >= 7 and best_state in STATE_CODES:
        chars = list(plate)
        # Position 2, 3: RTO number (digits)
        if len(chars) > 2 and chars[2] in CHAR_TO_NUM:
            chars[2] = CHAR_TO_NUM[chars[2]]
        if len(chars) > 3 and chars[3] in CHAR_TO_NUM:
            chars[3] = CHAR_TO_NUM[chars[3]]
            
        # Last 4 characters should be registration number (digits)
        for k in range(max(4, len(chars) - 4), len(chars)):
            if chars[k] in CHAR_TO_NUM:
                chars[k] = CHAR_TO_NUM[chars[k]]
                
        plate = "".join(chars)

    # Strip trailing single-character border/bolt noise (e.g. 'MH20DY23661' -> 'MH20DY2366')
    m_clean = re.match(r'^([A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4})[A-Z0-9]?$', plate)
    if m_clean:
        plate = m_clean.group(1)

    # Scoring
    if re.match(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$', plate):
        score += 100
    elif len(plate) >= 8 and best_state in STATE_CODES:
        score += 40
        
    score += len(plate) * 2
    region = STATE_MAP.get(best_state, "Unknown Region")
    return plate, region, best_state, score

def get_state_name(plate_number):
    """Returns (state_name, state_code)."""
    _, name, code, _ = sanitize_and_score_plate(plate_number)
    return name, code
