import uuid
import os
from config import TEMP_DIR
from fastapi import UploadFile
import shutil

def save_temp_audio(file : UploadFile) -> str:
    file_id = str(uuid.uuid4())
    file_path = os.path.join(TEMP_DIR, f"{file_id}_{file.filename}")

    # copy from source file to our temporary file little by little
    with open(file=file_path, mode="wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path