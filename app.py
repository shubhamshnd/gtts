from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
from pydub import AudioSegment
import os
import re
import threading
import uuid

app = Flask(__name__)

# Global variables to track progress and store file information
progress = 0
current_file = None

def text_to_speech(text, output_file):
    global progress, current_file
    
    # Split text into sentences
    sentences = [s.strip() for s in re.split('(?<=[.!?]) +', text) if s.strip()]
    
    # Create temporary directory for audio segments
    if not os.path.exists('temp_audio'):
        os.mkdir('temp_audio')
    
    combined = AudioSegment.empty()
    
    total_sentences = len(sentences)
    
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
        
        # Update progress
        progress = int((i + 1) / total_sentences * 100)
    
    # Export the final audio
    combined.export(output_file, format="mp3")
    
    # Clean up temporary files
    for file in os.listdir('temp_audio'):
        os.remove(os.path.join('temp_audio', file))
    os.rmdir('temp_audio')
    
    current_file = output_file

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tts', methods=['POST'])
def tts():
    global progress, current_file
    progress = 0
    
    text = request.form['text']
    filename = request.form['filename']
    
    if not filename.endswith('.mp3'):
        filename += '.mp3'
    
    output_file = os.path.join('static', filename)
    
    # Start TTS conversion in a separate thread
    thread = threading.Thread(target=text_to_speech, args=(text, output_file))
    thread.start()
    
    return jsonify({"message": "TTS conversion started", "filename": filename})

@app.route('/progress')
def get_progress():
    global progress
    return jsonify({"progress": progress})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join('static', filename), as_attachment=True)

@app.route('/play/<filename>')
def play_file(filename):
    return jsonify({"audio_url": f"/static/{filename}"})

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.mkdir('static')
    app.run(host='10.5.52.49', port=5000, debug=True)