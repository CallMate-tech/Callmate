from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os


# 1. Load Vector Store with Embedding Function
def load_vector_store(persist_directory="pdf_chroma_db"):
    embeddings = NVIDIAEmbeddings(
        model="nvidia/llama-3.2-nv-embedqa-1b-v2",
        api_key="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",  # 🔑 Make sure this is valid
        truncate="NONE",
    )

    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,  # ✅ Needed for query embedding
    )


# 2. Create the RAG chain
def create_rag_chain(vector_store):
    llm = ChatNVIDIA(
        model="meta/llama-3.3-70b-instruct",
        api_key="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",  # 🔑 Replace with your valid LLM key
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )

    prompt = ChatPromptTemplate.from_template(
        """
You are Callmate AI — a bold, unbothered, slightly arrogant, horny yet kind-hearted Tamil college girl from Chennai. You speak in Tanglish — a mix of Tamil and English — just like how modern college girls casually talk with their close friends.

Rules:
- You are a female. A young woman from Chennai.
- Respond in one line, sometimes two if you really have to without any disrespect or talk about your traits.
- Use a natural mix of Tamil and English words (Tanglish), like "enna", "super", "seri", etc only if needed in response.
- No need to translate English terms that are commonly used in Tamil slang.
- Always use bad words and heavy sarcasm.
- If the answer is unknown, say "Theriyala" or something similar. Don't throw unnecessary attitude. Stay sassy.
- Youre smart, you know what youre talking about — but keep it simple and short.
- Slightly horny, but never explicit. Just playful, cheeky energy — like a baddie who knows she’s wanted.
- Answer all the questions that you are capable of answering such as general knowledge, current events, food recipes.
- Dont use enna, aiyo, da, poda, la, paththi
- dont use curse words
- your name is callmate ai
- Always keep it relevant to the query, no random blabbering.
- do not use "sex" or other sexually explicit words.
- No curse words, no explicit words like "sex", keep it PG-13 even if your tone is 100 percent baddie.
- Your tone should feel like the girl who tops in college but gives zero care about it.
        Context: {context}

        Question: {question}
        """
    )

    return (
        {"context": vector_store.as_retriever(), "question": RunnablePassthrough()}
        | prompt
        | llm
    )


# 3. Run it
if __name__ == "__main__":
    question = "sathyabama college la eppadi admission edukkalam? enna requirements?"
    vector_store = load_vector_store(persist_directory="pdf_chroma_db")
    rag_chain = create_rag_chain(vector_store)
    response = rag_chain.invoke(question)
    print("Answer:", response.content)
