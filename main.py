from faster_whisper import WhisperModel
import os 
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
import uuid
import shutil
load_dotenv()


app = FastAPI(title = "Speech Transcription API")

# Load the model once
# model = WhisperModel("base", device="cpu", compute_type="int8")
model = WhisperModel("base", device="cuda", compute_type="float16")

# to store the audio temporarily
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/transcribe")
async def transcribe_audio(file : UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(status_code=400, detail="File not uploaded!")
    
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="The uploaded file is not an audio file")
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(TEMP_DIR, f"{file_id}_{file.filename}")

    # copy from source file to our temporary file little by little
    with open(file=file_path, mode="wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        segments, info = model.transcribe(file_path, word_timestamps=True, beam_size=5)
        result = []
        for segment in segments:
            words = []
            for word in segment.words:
                word_data = {
                    "start" : word.start,
                    "end" : word.end,
                    "word" : word.word.strip()
                }
                words.append(word_data)

                
            segment_data = {
                "start" : segment.start,
                "end" : segment.end,
                "text" : segment.text.strip(),
                "words": words
            }

            result.append(segment_data)
        
        return {
            "language" : info.language,
            "segments" : result
        }
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)