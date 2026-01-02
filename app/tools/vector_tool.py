from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from app.core import settings
import os

def search_vector_db(query_text):
    if not os.path.exists(settings.VECTOR_INDEX_PATH):
        return []

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = FAISS.load_local(settings.VECTOR_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    results = vector_db.similarity_search(query_text, k=5)
    return results
