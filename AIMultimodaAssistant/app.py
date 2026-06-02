import os
import cv2
import time
import json
import queue
import wave
import requests
import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import whisper
import gradio as gr
import pyaudio

from PIL import Image
from dotenv import load_dotenv
from pydub import AudioSegment





# ==========================================================
# Load Whisper Model
# ==========================================================

print("Loading Whisper model...")
whisper_model = whisper.load_model("base")

# ==========================================================
# Audio Recording
# ==========================================================

SAMPLE_RATE = 44100
CHANNELS = 1

def record_audio(duration=5, filename="recorded_audio.wav"):
    print("Recording started...")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='int16'
    )

    sd.wait()

    sf.write(filename, audio, SAMPLE_RATE)

    print("Recording completed.")

    return filename

# ==========================================================
# Speech Recognition (Google API)
# ==========================================================

def speech_to_text_google(audio_path):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except Exception as e:
        return f"SpeechRecognition Error: {e}"

# ==========================================================
# Whisper Transcription
# ==========================================================

def whisper_transcribe(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

# ==========================================================
# Webcam Capture using OpenCV
# ==========================================================

def capture_image():
    filename = "captured_image.jpg"
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        return None

    ret, frame = cam.read()

    if ret:
        
        cv2.imwrite(filename, frame)

    cam.release()

    return filename

# ==========================================================
# Image Processing with Pillow
# ==========================================================

def process_image(image_path):
    image = Image.open(image_path)

    # Resize image
    image = image.resize((300, 300))

    processed_path = "processed_image.png"
    image.save(processed_path)

    return processed_path

# ==========================================================
# Ollama Local LLM
# ==========================================================

def ask_ollama(prompt):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()["response"]

    return "Ollama Error"


# ==========================================================
# Audio Playback using PyAudio
# ==========================================================

def play_audio(audio_path):
    chunk = 1024

    wf = wave.open(audio_path, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )

    data = wf.readframes(chunk)

    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    stream.stop_stream()
    stream.close()

    p.terminate()

# ==========================================================
# Convert Audio using pydub
# ==========================================================

def convert_audio(audio_path):
    sound = AudioSegment.from_wav(audio_path)

    mp3_path = "converted_audio.mp3"

    sound.export(mp3_path, format="mp3")

    return mp3_path

# ==========================================================
# Complete AI Pipeline
# ==========================================================

def full_pipeline(duration):

    # Record
    audio_path = record_audio(duration)

    # SpeechRecognition
    google_text = speech_to_text_google(audio_path)

    # Whisper
    whisper_text = whisper_transcribe(audio_path)

    # Ollama
    ollama_response = ask_ollama(whisper_text)



    # Webcam
    image_path = capture_image()

    processed_image = None

    if image_path:
        processed_image = process_image(image_path)

    # Convert Audio
    mp3_path = convert_audio(audio_path)

    return (
        audio_path,
        mp3_path,
        google_text,
        whisper_text,
        ollama_response,
        processed_image
    )

# ==========================================================
# Gradio Interface
# ==========================================================

interface = gr.Interface(
    fn=full_pipeline,
    inputs=gr.Slider(1, 10, value=5, label="Recording Duration"),
    outputs=[
        gr.Audio(label="Recorded Audio"),
        gr.Audio(label="Converted MP3"),
        gr.Textbox(label="Google Speech Recognition"),
        gr.Textbox(label="Whisper Transcription"),
        gr.Textbox(label="Ollama Response"),
        gr.Image(label="Processed Webcam Image")
    ],
    title="AI Multimodal Assistant",
    description="Speech + Vision + Ollama + Whisper"
)

# ==========================================================
# Run App
# ==========================================================

if __name__ == "__main__":
    interface.launch()