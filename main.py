import os
import time
import math
import hashlib
import json
from typing import List
import streamlit as st
from PyPDF2 import PdfReader
import numpy as np
import faiss
import openai
from dotenv import load_dotenv

# Optional: Local embedding model
LOCAL_EMBEDDINGS_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    LOCAL_EMBEDDINGS_AVAILABLE = True
except ImportError:
    pass

# Load environment variables
load_dotenv()

# Get API key from environment or Streamlit secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("Please set the OPENAI_API_KEY in environment variables or Streamlit secrets.")
    st.stop()

openai.api_key = OPENAI_API_KEY

# -------- Embedding Function --------
def get_embeddings(texts: List[str]) -> np.ndarray:
    if LOCAL_EMBEDDINGS_AVAILABLE:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(texts)
    else:
        resp = openai.Embedding.create(
            input=texts,
            model="text-embedding-ada-002"
        )
        return np.array([d["embedding"] for d in resp["data"]])

# -------- PDF Loader --------
def load_pdf(file) -> str:
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text.strip()

# -------- Chunk Text --------
def chunk_text(text: str, chunk_size=500, overlap=50) -> List[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# -------- Create Vector Store --------
def create_vectorstore(chunks: List[str]):
    embeddings = get_embeddings(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index, chunks

# -------- Search Similar Chunks --------
def search_chunks(query: str, index, chunks, top_k=3) -> List[str]:
    query_emb = get_embeddings([query])
    distances, indices = index.search(query_emb, top_k)
    results = [chunks[i] for i in indices[0] if i < len(chunks)]
    return results

# -------- Chat Function --------
def chat_with_pdf(question: str, index, chunks) -> str:
    similar_chunks = search_chunks(question, index, chunks)
    context = "\n\n".join(similar_chunks)
    prompt = f"Answer the question based on the following context:\n{context}\n\nQuestion: {question}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for answering questions from PDF content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    return response["choices"][0]["message"]["content"].strip()

# -------- Streamlit UI --------
st.set_page_config(page_title="PDF Q&A Chatbot", layout="wide")
st.title("📄 PDF Q&A Chatbot")

uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
if uploaded_file:
    with st.spinner("Processing PDF..."):
        pdf_text = load_pdf(uploaded_file)
        if not pdf_text:
            st.error("No extractable text found in PDF.")
            st.stop()
        chunks = chunk_text(pdf_text)
        index, chunk_list = create_vectorstore(chunks)
    st.success("PDF processed successfully!")

    question = st.text_input("Ask a question about the PDF:")
    if question:
        with st.spinner("Generating answer..."):
            answer = chat_with_pdf(question, index, chunk_list)
        st.markdown(f"**Answer:** {answer}")
  
