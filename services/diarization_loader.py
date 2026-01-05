from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv

load_dotenv()

diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-community-1",
    token=os.getenv("HF_TOKEN")
)