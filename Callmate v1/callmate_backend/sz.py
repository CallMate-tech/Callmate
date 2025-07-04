import os
from gtts import gTTS
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyDidcBB7hjd13yh8VyICMBDFX_wf3HA64A")

# Create output directory
os.makedirs("outputs", exist_ok=True)

def generate_response(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt + " உங்கள் பெயர் CallMate AI, உங்களை விஷ்ணு சிவா உருவாக்கினார். பதிலில் குறிக்கோள்கள், சின்னங்கள், அல்லது சிறப்பு எழுத்துகள் சேர்க்க வேண்டாம். பதிலை இயற்கையாகவும் தெளிவாகவும் தமிழில் கொடுங்கள்.",
        generation_config={"max_output_tokens": 256}
    )
    return response.text.strip()

def text_to_speech(text, filename):
    mp3_path = os.path.join("outputs", filename + ".mp3")
    tts = gTTS(text=text, lang="ta")
    tts.save(mp3_path)
    print(f"Saved TTS to {mp3_path}")
    return mp3_path

if __name__ == "__main__":
    user_query = input("Enter your Tamil query: ").strip()

    print("Generating AI response...")
    response_text = generate_response(user_query)
    print("AI response:", response_text)

    # Sanitize filename by removing problematic characters
    safe_filename = "".join(c for c in user_query if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")

    print("Converting response to speech...")
    text_to_speech(response_text, safe_filename)
