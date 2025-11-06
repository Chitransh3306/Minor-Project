import os
import tempfile

def save_temp_image(uploaded_file):
    """Save uploaded file temporarily and return its path."""
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path
