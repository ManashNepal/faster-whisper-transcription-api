import os
import uuid
import torchaudio
import soundfile as sf
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File

from model_loader import model
from services.audio_validate import validate_audio
from services.save_temp_audio import save_temp_audio
from services.diarization_loader import diarization_pipeline
from services.convert_audio import convert_to_wav

load_dotenv()

app = FastAPI(title="Speech Transcription API with Speaker Diarization")

def save_segment_wav(waveform, sample_rate):
    path = os.path.join("temp_audio", f"segment_{uuid.uuid4().hex}.wav")
    sf.write(path, waveform.squeeze().numpy(), sample_rate)
    return path

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    validate_audio(file)

    original_path = save_temp_audio(file)
    wav_path = None

    try:
        # Normalize audio (MP3 to WAV)
        wav_path = convert_to_wav(original_path)

        # Load audio for diarization
        waveform, sample_rate = torchaudio.load(wav_path)

        diarization = diarization_pipeline({
            "waveform": waveform,
            "sample_rate": sample_rate
        })

        results = []
        language = None

        # Process each speaker segment
        for turn, speaker in diarization.speaker_diarization:
            start_sample = int(turn.start * sample_rate)
            end_sample = int(turn.end * sample_rate)

            segment_waveform = waveform[:, start_sample:end_sample]

            # skip very short segments(<0.3s)
            if segment_waveform.shape[1] < int(sample_rate * 0.3):
                continue

            segment_path = save_segment_wav(segment_waveform, sample_rate)

            try:
                segments, info = model.transcribe(
                    segment_path,
                    word_timestamps=True,
                    beam_size=5
                )

                language = info.language

                text = " ".join(seg.text for seg in segments).strip()

                if text:
                    results.append({
                        "speaker": f"speaker_{speaker}",
                        "start": round(turn.start, 2),
                        "end": round(turn.end, 2),
                        "text": text
                    })

            finally:
                if os.path.exists(segment_path):
                    os.remove(segment_path)

        return {
            "language": language,
            "segments": results
        }

    finally:
        for path in [original_path, wav_path]:
            if path and os.path.exists(path):
                os.remove(path)
