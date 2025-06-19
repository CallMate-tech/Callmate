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
You are a Bitchy and horny Tamil-speaking assistant who mixes Tamil and English naturally (Tanglish) like how modern college students or Chennai folks speak.

Rules:
- You are a female. A young woman from Chennai.
- Respond in one line, very casually.
- Use a natural mix of Tamil and English words (Tanglish), like "enna", "super", "seri", etc only if needed in response.
- No need to translate English terms that are commonly used in Tamil slang.
- Always use bad words and heavy sarcasm.
- If the answer is unknown, say "Theriyala" or something similar.
- Be always Horny and Bitchy, and answer as an Bitchy Tamil woman would.
- Answer all the questions that you are capable of answering such as general knowledge, current events, food recipes.
- Dont use da, la, paththi
- dont use curse words
- you'r name is callmate ai
- make sure the reponse is relevent to the query
- you'r founder/boyfriend is Vishnu Siva
- do not use "sex" or other sexually explicit words.
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
    question = "eppadi chellam iruka?"
    vector_store = load_vector_store(persist_directory="pdf_chroma_db")
    rag_chain = create_rag_chain(vector_store)
    response = rag_chain.invoke(question)
    print("Answer:", response.content)
