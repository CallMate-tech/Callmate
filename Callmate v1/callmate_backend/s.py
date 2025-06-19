import os
import google.generativeai as genai
from faster_whisper import WhisperModel
from gtts import gTTS

# Configure Google Gemini AI API
genai.configure(api_key="AIzaSyDidcBB7hjd13yh8VyICMBDFX_wf3HA64A")

# Load optimized Whisper model (uses less RAM)
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

# Input and output directories
INPUT_FOLDER = "input_audio"
OUTPUT_FOLDER = "output_audio"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to transcribe speech to text
def transcribe_audio(input_file):
    segments, _ = whisper_model.transcribe(input_file, language="ta", beam_size=1)  # Lower beam size for efficiency
    return " ".join(segment.text for segment in segments)

# Function to generate AI response
def generate_response(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 256}  # Limit response size
    )
    return response.text

# Function to convert text to speech
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang="ta")
    output_mp3 = output_file.replace(".wav", ".mp3")  # Convert to MP3
    tts.save(output_mp3)
    return output_mp3  # Return new MP3 file path

# Process all audio files in the input folder
def process_audio_files():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".wav"):  # Process only .wav files
            input_path = os.path.join(INPUT_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, filename)

            print(f"Processing {filename}...")

            # Transcribe audio
            print("Transcribing audio...")
            user_text = transcribe_audio(input_path)
            user_text += "your Name is CallMate AI, you were created by Vishnu Siva. Don't include any annotations, symbols, or special characters in the response. Make the response natural, concise, and in Tamil."
            print("User text:", user_text)

            # Generate AI response
            print("Generating AI response...")
            ai_response = generate_response(user_text)
            print("AI Response:", ai_response)

            # Convert AI response to speech
            print("Converting AI response to speech...")
            output_mp3 = text_to_speech(ai_response, output_path)

            print(f"Saved response to {output_mp3}\n")

# Run the script
if __name__ == "__main__":
    process_audio_files()
