import os
import soundfile as sf
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File

from model_loader import model
from services.audio_validate import validate_audio
from services.save_temp_audio import save_temp_audio

load_dotenv()

app = FastAPI(title="Speech Transcription API with Speaker Diarization")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    validate_audio(file)

    file_path = save_temp_audio(file)

    try:
        segments, info = model.transcribe(
                        file_path,
                        beam_size=5
                    )

        whisper_info = []

        for segment in segments:
            whisper_info.append({
                "start" : round(segment.start, 2),
                "end" : round(segment.end, 2),
                "text" : segment.text.strip()
            })
        
        return {
            "language" : info.language,
            "segments" : whisper_info
        }

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)