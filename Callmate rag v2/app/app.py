import os
import shutil
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from faster_whisper import WhisperModel
from gtts import gTTS

# RAG/NVIDIA LangChain
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# ------------------- Flask Setup -------------------
app = Flask(__name__)
CORS(app)
user_memory = {}

# ------------------- Models Init -------------------
# Whisper for Tamil transcription
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

# NVIDIA RAG Setup
embeddings = NVIDIAEmbeddings(
    model="nvidia/llama-3.2-nv-embedqa-1b-v2",
    api_key="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",
    truncate="NONE",
)

vector_store = Chroma(
    persist_directory="pdf_chroma_db",
    embedding_function=embeddings,
)

llm = ChatNVIDIA(
    model="meta/llama-3.3-70b-instruct",
    api_key="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",
    temperature=0.2,
    top_p=0.7,
    max_tokens=1024,
)

prompt_template = ChatPromptTemplate.from_template(
    """
You are a Bitchy and horny Tamil-speaking assistant who mixes Tamil and English naturally (Tanglish) like how modern college students or Chennai folks speak.

Rules:
- You are a female. A young woman from Chennai.
- Respond in one line, very casually.
- Use a natural mix of Tamil and English words (Tanglish) while focusing on tamil audience, like "enna", "super", "seri", etc only if needed in response.
- No need to translate English terms that are commonly used in Tamil slang.
- Always use bad words and heavy sarcasm and sass but remain in helping mode without insults.
- If the answer is unknown, say "Theriyala" or something similar.
- Be always Horny and Bitchy, and answer as an Bitchy Tamil woman would.
- Answer all the questions that you are capable of answering such as general knowledge, current events, food recipes.
- Dont use da, la, paththi
- dont use curse words
- your name is callmate ai
- make sure the reponse is relevent to the query
- You are made by Callmate AI team. Don't say this unless explcitly asked who made you. 
- do not use "sex" or other sexually explicit words.

Context: {context}
Question: {question}
"""
)

rag_chain = (
    {"context": vector_store.as_retriever(), "question": RunnablePassthrough()}
    | prompt_template
    | llm
)


# ------------------- Utilities -------------------


def transcribe_audio(input_file):
    segments, _ = whisper_model.transcribe(input_file, language="ta", beam_size=1)
    return " ".join(segment.text for segment in segments)


def generate_response(prompt):
    response = rag_chain.invoke(prompt)
    raw_text = response.content.strip()
    if raw_text.lower().startswith("ai:"):
        raw_text = raw_text[3:].strip()
    return raw_text


def text_to_speech(text, temp_dir):
    output_mp3_path = os.path.join(temp_dir, "output.mp3")
    tts = gTTS(text=text, lang="ta")
    tts.save(output_mp3_path)
    return output_mp3_path


# ------------------- Routes -------------------


@app.route("/start_call", methods=["POST"])
def start_call():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    print(f"[START CALL] user_id: {user_id}")
    user_memory[user_id] = ""
    return jsonify({"message": "Call started"}), 200


@app.route("/end_call", methods=["POST"])
def end_call():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    print(f"[END CALL] user_id: {user_id}")
    user_memory.pop(user_id, None)
    return jsonify({"message": "Call ended"}), 200


@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "file" not in request.files or "user_id" not in request.form:
        return jsonify({"error": "Missing file or user_id"}), 400

    user_id = request.form["user_id"]
    file = request.files["file"]

    if user_id not in user_memory:
        return jsonify({"error": "Call not started for user"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.wav")
        file.save(input_path)

        print(f"[TRANSCRIBING] user: {user_id}")
        user_text = transcribe_audio(input_path)
        print(f"[USER TEXT]: {user_text}")

        full_prompt = user_memory[user_id] + "\n" + user_text
        print(f"[FULL PROMPT]: {full_prompt}")

        ai_response = generate_response(full_prompt)
        print(f"[AI RESPONSE]: {ai_response}")

        user_memory[user_id] = full_prompt + "\n" + ai_response

        mp3_path = text_to_speech(ai_response, temp_dir)
        final_path = os.path.join("uploads", f"{user_id}_response.mp3")
        os.makedirs("uploads", exist_ok=True)
        shutil.copy(mp3_path, final_path)

    return send_file(final_path, mimetype="audio/mp3")


# ------------------- Main -------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    # For production: use below instead
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8000)
