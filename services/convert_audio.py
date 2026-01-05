import subprocess
import os

def convert_to_wav(input_path: str) -> str:
    """
    Converts input audio(mp3/wav) to mono 16kHz WAV.
    Returns path to WAV file.
    """
    output_path = input_path.rsplit(".", 1)[0] + ".wav"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            output_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return output_path
