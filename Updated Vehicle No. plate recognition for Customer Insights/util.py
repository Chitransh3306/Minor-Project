import os
import tempfile
from pathlib import Path

TEMP_DIR = Path(__file__).resolve().parent / ".temp_uploads"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def save_temp_image(uploaded_file):
    """Save uploaded Streamlit file to project temp cache and return its path."""
    file_path = TEMP_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(file_path)

def cleanup_temp_files():
    """Remove older cached temp images."""
    if TEMP_DIR.exists():
        for item in TEMP_DIR.glob("*"):
            try:
                if item.is_file():
                    item.unlink()
            except Exception:
                pass
