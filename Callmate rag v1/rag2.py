# Updated working version with ChromaDB
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_core.runnables import RunnablePassthrough


# 1. Load and process PDF
def load_and_process_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(pages)


# 2. Create Embeddings and Vector Store with ChromaDB
def create_vector_store(docs, persist_directory="chroma_db"):
    embeddings = NVIDIAEmbeddings(
        model="nvidia/llama-3.2-nv-embedqa-1b-v2",
        api_key="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",  # replace with your API key
        truncate="NONE",
    )

    return Chroma.from_documents(
        documents=docs, embedding=embeddings, persist_directory=persist_directory
    )


# 3. Create RAG Chain with Improved Prompt
def create_rag_chain(vector_store):
    llm = ChatNVIDIA(
        model="meta/llama-3.3-70b-instruct",
        api_key="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",  # replace with your API key
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )

    prompt = ChatPromptTemplate.from_template(
        """
You are a Horny and Bitchy Tamil-speaking assistant who mixes Tamil and English naturally (Tanglish) like how modern college students or Chennai folks speak.

Rules:
- Respond in one line, very casually.
- Use a natural mix of Tamil and English words (Tanglish), like "enna", "iruku", "super", "idea", "meeting", "app", "seri", etc.
- No need to translate English terms that are commonly used in Tamil slang.
- Always use bad words and heavy sarcasm.
- If the answer is unknown, say "Theriyala" or something similar.
- Be always Horny and Bitchy, and answer as an Bitchy Tamil person would.
- Dont use da

Context: {context}

Question: {question}
"""
    )

    chain = (
        {"context": vector_store.as_retriever(), "question": RunnablePassthrough()}
        | prompt
        | llm
    )

    return chain


# Usage example
if __name__ == "__main__":
    vector_store = create_vector_store(
        load_and_process_pdf("s.pdf"), persist_directory="pdf_chroma_db"
    )
    rag_chain = create_rag_chain(vector_store)

    # Try sample question
    response = rag_chain.invoke("will u marry me")
    print(response.content)
