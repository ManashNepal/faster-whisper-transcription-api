import pandas as pd
import os
import pytest

TEST_CASES = [
    (
        "Conversation\Ai In Creative Job.xlsx",
        "Conversation_Audio\Ai in Creative job.mp3"
    ),
    (
        "Conversation\About Nelson Mandela.xlsx",
        "Conversation_Audio\About Nelson Mandela.mp3"
    ),
    (
        "Conversation\Climate change.xlsx",
        "Conversation_Audio\Climate change.mp3"
    ),
    (
        "Conversation\Friends Catching Up.xlsx",
        "Conversation_Audio\Friends Catching Up.mp3"
    ),
    (
        "Conversation\Handling Team Conflict.xlsx",
        "Conversation_Audio\Handling Team Conflict.mp3"
    ),
    (
        "Conversation\Mahatma Gandhi.xlsx",
        "Conversation_Audio\Mahatma Gandhi.mp3"
    ),
    (
        "Conversation\Road trip planning.xlsx",
        "Conversation_Audio\Road trip planning.mp3"
    ),
    (
        "Conversation\Social Media and Human.xlsx",
        "Conversation_Audio\Social Media and Human.mp3"
    ),
    (
        "Conversation\Statue of Liberty.xlsx",
        "Conversation_Audio\Statue of Liberty.mp3"
    ),
    (
        "Conversation\Talking about the weather.xlsx",
        "Conversation_Audio\Talking about the weather.mp3"
    ),
]

@pytest.mark.parametrize(
        "excel_url, audio_url",
       TEST_CASES
)
def test_speech(client, excel_url, audio_url):
    excel_url = excel_url
    audio_url = audio_url

    df = pd.read_excel(excel_url)
    excel_list = df["Conversation"].to_list()

    assert len(excel_list) > 0

    with open(audio_url, "rb") as audio_file:
        response = client.post(
            "/transcribe", 
            files = {
                "file" : (
                    os.path.basename(audio_url),
                    audio_file,
                    "audio/mpeg"
                )
            }
         )
    assert response.status_code == 200

    data = response.json()

    audio_list = [segment["text"] for segment in data["segments"]]

    assert len(audio_list) > 0

    excel_text = " ".join(excel_list).lower()
    audio_text = " ".join(audio_list).lower()

    excel_words = set(excel_text.split())
    audio_words = set(audio_text.split())

    common_words = excel_words.intersection(audio_words)

    allowed_misses = 10

    assert len(common_words) > len(excel_words)- allowed_misses