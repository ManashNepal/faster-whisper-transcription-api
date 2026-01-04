from fastapi import UploadFile, HTTPException

def validate_audio(file : UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File not uploaded!")
    
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="The uploaded file is not an audio file")