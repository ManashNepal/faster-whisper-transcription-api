import pandas as pd
import os
import pytest
import re
from difflib import SequenceMatcher

def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity ratio between two strings (0.0 to 1.0)"""
    return SequenceMatcher(None, str1, str2).ratio()

def find_best_match(expected_line: str, api_segments: list, start_idx: int = 0, max_combine: int = 3):
    expected_clean = remove_special_characters(expected_line).lower()
    best_similarity = 0.0
    best_match = None
    best_indices = []
    
    # Try combining 1 to max_combine consecutive segments
    for combine_count in range(1, min(max_combine + 1, len(api_segments) - start_idx + 1)):
        for i in range(start_idx, len(api_segments) - combine_count + 1):
            # Combine consecutive segments
            combined_text = " ".join([api_segments[j]["text"] for j in range(i, i + combine_count)])
            combined_clean = remove_special_characters(combined_text).lower()
            
            similarity = calculate_similarity(expected_clean, combined_clean)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = combined_text
                                                                             
    return best_match, best_similarity, best_indices

def remove_special_characters(sentence : str) -> str:
    res = re.sub(r'[^a-zA-Z0-9]', '', sentence)

    return res

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

    api_segments = data["segments"]

    used_segments = set()
    mismatches = []
    
    for line_num, expected_line in enumerate(excel_list, start=1):  
        best_match, similarity, segment_indices = find_best_match(
            expected_line, 
            api_segments,
            start_idx=0,
            max_combine=3
        )
        
        if similarity >= 0.95:
            used_segments.update(segment_indices)
        else:
            mismatches.append({
                'line_num': line_num,
                'expected': expected_line,
                'best_match': best_match,
                'similarity': similarity
            })
    
    if mismatches:
        print("\n")
        print("-"*80)
        print(f"Mismatches found in {os.path.basename(audio_url)}:")
        print("-"*80)
        for mismatch in mismatches:
            print(f"\nLine {mismatch['line_num']}:")
            print(f"Expected: {mismatch['expected']}")
            print(f"Got: {mismatch['best_match']}")
            print(f"Similarity: {mismatch['similarity']:.2%}")
    if len(mismatches) > 0:
        print(f"Found {len(mismatches)} mismatched lines\n")
        
    assert len(mismatches) == 0