import pyaudio
import wave
import numpy as np
import librosa
import vosk
import json
from flask import Flask, render_template, request, Response

app = Flask(__name__, template_folder="path")

model_path = r"C:\Users\xyz\Desktop\vosk-model-en-us-0.22-lgraph"
model = vosk.Model(model_path)
recognizer = vosk.KaldiRecognizer(model, 16000)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

real_time_transcription = ""  # Initialize real-time transcription variable

@app.route('/')
def index():
    return render_template('index.html')

def process_audio(data):
    recognizer.AcceptWaveform(data)
    result = recognizer.Result()
    result_json = json.loads(result)
    return result_json['text']

def generate_audio():
    while True:
        data = stream.read(CHUNK)
        transcription = process_audio(data)
        global real_time_transcription
        real_time_transcription = transcription  # Update the real-time transcription
        yield f"data:{transcription}\n\n"

@app.route('/audio_feed')
def audio_feed():
    return Response(generate_audio(), mimetype='text/event-stream')

@app.route('/get_audio')
def get_audio():
    global real_time_transcription
    return Response(real_time_transcription, mimetype='text/plain')

@app.route('/save_transcript', methods=['POST'])
def save_transcript():
    data = request.get_json()
    transcript = data.get('transcript', '')
    
    if transcript:
        with open('transcript.txt', 'a') as file:
            file.write(transcript + "\n")
        return jsonify({'message': 'Transcript saved successfully'}), 200
    return jsonify({'message': 'No transcript provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
