import os
from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
from faster_whisper import WhisperModel
from gtts import gTTS

# pip install Flask google-generativeai faster-whisper gtts

app = Flask(__name__)

# Load Models
whisper_model = WhisperModel("medium", device="cpu", compute_type="int8")
genai.configure(api_key="AIzaSyDidcBB7hjd13yh8VyICMBDFX_wf3HA64A")

# Function to convert speech to text
def transcribe_audio(input_file):
    segments, _ = whisper_model.transcribe(input_file, language="ta")
    return " ".join([segment.text for segment in segments])

# Function to generate AI response
def generate_response(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang="ta")  # 'ta' for Tamil
    tts.save(output_file)



@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    input_path = "uploads/input.wav"
    output_path = "uploads/output.wav"
    os.makedirs("uploads", exist_ok=True)
    file.save(input_path)

    # Process audio
    print("Transcribing audio...")
    user_text = transcribe_audio(input_path)+" Your Name is CallMate ai, you were created by Vishnu Siva. Dont include any annotations or symbols or any special characters in response and make the response more human like natural and kmake the resposne consise and clear and understandable and up to the point and make it as sounds like an conversation and the response to be in an paragraph and it need to be in tamil language"
    print(user_text)
    print("Generating AI response...")
    ai_response = generate_response(user_text)
    print(ai_response)
    print("Converting AI response to speech...")
    text_to_speech(ai_response, output_path)

    return send_file(output_path, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
