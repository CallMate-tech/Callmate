import os
import tempfile
import shutil
from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
from faster_whisper import WhisperModel
from gtts import gTTS
from waitress import serve

app = Flask(__name__)

# Load Whisper model
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

# Configure Google Gemini API
genai.configure(api_key="AIzaSyDidcBB7hjd13yh8VyICMBDFX_wf3HA64A")


# Transcribe Tamil audio
def transcribe_audio(input_file):
    segments, _ = whisper_model.transcribe(input_file, language="ta", beam_size=1)
    return " ".join(segment.text for segment in segments)


# Generate AI response
def generate_response(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt, generation_config={"max_output_tokens": 256}
    )
    return response.text


# Convert text to Tamil speech using gTTS (return MP3 path)
def text_to_speech(text, temp_dir):
    output_mp3_path = os.path.join(temp_dir, "output.mp3")
    tts = gTTS(text=text, lang="ta")
    tts.save(output_mp3_path)
    return output_mp3_path


@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.wav")
        file.save(input_path)

        print("Transcribing audio...")
        user_text = transcribe_audio(input_path)
        user_text += (
            "Your Name is CallMate AI, you were created by CallMate Team "
            "Don't include any annotations, symbols, or special characters in the response. "
            "Make the response natural, concise, and in Tamil."
        )
        print("Prompt:", user_text)

        print("Generating AI response...")
        ai_response = generate_response(user_text)
        print("AI response:", ai_response)

        print("Converting AI response to speech...")
        mp3_path = text_to_speech(ai_response, temp_dir)

        # Copy to a non-temp path before the temp dir gets deleted
        final_path = os.path.join("uploads", "response.mp3")
        os.makedirs("uploads", exist_ok=True)
        shutil.copy(mp3_path, final_path)

    return send_file(final_path, mimetype="audio/mp3")


# Start server
if __name__ == "__main__":
    # serve(app, host="0.0.0.0", port=8000, threads=2)
    app.run(debug=True)
