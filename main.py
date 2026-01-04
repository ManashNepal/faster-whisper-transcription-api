import os 
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from config import TEMP_DIR
from model_loader import model
from services.audio_validate import validate_audio
from services.save_temp_audio import save_temp_audio
from services.build_response import build_response
load_dotenv()


app = FastAPI(title = "Speech Transcription API")

@app.post("/transcribe")
async def transcribe_audio(file : UploadFile = File(...)):       
    validate_audio(file)
    file_path = save_temp_audio(file)
    
    try:
        segments, info = model.transcribe(file_path, word_timestamps=True, beam_size=5)
        result = build_response(segments)        
        return {
            "language" : info.language,
            "segments" : result
        }
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)