from gtts import gTTS
from pydub import AudioSegment
import os
import re

def text_to_speech(text, output_file):
    # Split text into sentences
    sentences = [s.strip() for s in re.split('(?<=[.!?]) +', text) if s.strip()]
    
    # Create temporary directory for audio segments
    if not os.path.exists('temp_audio'):
        os.mkdir('temp_audio')
    
    combined = AudioSegment.empty()
    
    for i, sentence in enumerate(sentences):
        if sentence:
            try:
                tts = gTTS(sentence, lang='en', slow=False)
                temp_file = f'temp_audio/sentence_{i}.mp3'
                tts.save(temp_file)
                segment = AudioSegment.from_mp3(temp_file)
                combined += segment
            except AssertionError:
                print(f"Skipping empty sentence: {sentence}")
        
        # Add a short pause between sentences
        combined += AudioSegment.silent(duration=300)  # 300ms pause
    
    # Export the final audio
    combined.export(output_file, format="mp3")
    
    # Clean up temporary files
    for file in os.listdir('temp_audio'):
        os.remove(os.path.join('temp_audio', file))
    os.rmdir('temp_audio')

# Example usage
text = """



"""

output_file = "ribintro.mp3"
text_to_speech(text, output_file)
print(f"Audio saved to {output_file}")
