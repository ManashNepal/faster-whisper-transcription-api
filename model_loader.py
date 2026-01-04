from faster_whisper import WhisperModel

# Load the model once
# model = WhisperModel("base", device="cpu", compute_type="int8")
model = WhisperModel("base", device="cuda", compute_type="float16")