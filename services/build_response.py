def build_response(segments):
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
    return result