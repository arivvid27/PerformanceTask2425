import os
import tempfile
from datetime import datetime

def generate_filename(prefix="audio", extension="mp3"):
    """Generate a unique filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def save_uploaded_file(file, directory="uploads"):
    """Save an uploaded file and return the path."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filename = generate_filename()
    filepath = os.path.join(directory, filename)
    file.save(filepath)
    return filepath

def create_temp_file(content, extension="txt"):
    """Create a temporary file with the given content."""
    temp_file = tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False)
    
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    temp_file.write(content)
    temp_file.close()
    return temp_file.name