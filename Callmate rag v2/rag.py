# Updated working version with ChromaDB
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_core.runnables import RunnablePassthrough


# 1. Load and process PDF (same as before)
def load_and_process_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(pages)


# 2. Create Embeddings and Vector Store with ChromaDB
def create_vector_store(docs, persist_directory="chroma_db"):
    embeddings = NVIDIAEmbeddings(
        model="nvidia/llama-3.2-nv-embedqa-1b-v2",
        api_key="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",
        truncate="NONE",
    )

    return Chroma.from_documents(
        documents=docs, embedding=embeddings, persist_directory=persist_directory
    )


# 3. Create RAG Chain (fixed version)
def create_rag_chain(vector_store):
    llm = ChatNVIDIA(
        model="meta/llama-3.3-70b-instruct",
        api_key="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",
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )

    prompt = ChatPromptTemplate.from_template(
        """
    Use the following context to answer the question.
    If you don't know the answer, say you don't know.
    Keep the answer concise and direct. Do not include special charecteristics in your answer.
    And give the answer in a single line and in the mix of tamil and english like how normal tamil person speaks. just answer for what the question needs dont anser more or less.
     you can speak badwords also if needed. you will mock the user if the question is not good.
    Context: {context}

    Question: {question}
    """
    )

    # Create the chain with proper input formatting
    chain = (
        {"context": vector_store.as_retriever(), "question": RunnablePassthrough()}
        | prompt
        | llm
    )

    return chain


# Usage example
if __name__ == "__main__":
    # Process PDF and create/load vector store
    vector_store = create_vector_store(
        load_and_process_pdf("s.pdf"), persist_directory="pdf_chroma_db"
    )

    # Create RAG chain
    rag_chain = create_rag_chain(vector_store)

    # Ask a question (note the input key is now 'question')
    response = rag_chain.invoke("will u marry me")
    print(response.content)

# use words like "enna", "idhu", "iruku" if needed alone don't use unnecessarily
