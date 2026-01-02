import os
import glob
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

LOCAL_SERVER_URL = "http://localhost:1234/v1"

LM_STUDIO_DIR = r"C:\Users\iyedm\.lmstudio\models\lmstudio-community"

def find_gguf(folder_name):
    search_path = os.path.join(LM_STUDIO_DIR, folder_name, "*.gguf")
    files = glob.glob(search_path)
    if files:
        return files[0] 
    return None

MODEL_ROUTER_PATH = find_gguf("Qwen3-4B-Instruct-2507-GGUF")

MODEL_CHUNKING_PATH = None 

MODEL_RERANKER_PATH = find_gguf("Qwen3-4B-Instruct-2507-GGUF")

MODEL_CODER = "llama-3.3-70b-versatile"
MODEL_WRITER = "llama-3.3-70b-versatile"

DATA_PATH = os.path.join(os.getcwd(), "data", "raw_docs")
VECTOR_INDEX_PATH = os.path.join(os.getcwd(), "data", "index", "vector_store.faiss")

if __name__ == "__main__":
    print(f"Router (Local File): {MODEL_ROUTER_PATH}")
    print(f"Chunking (Via Server): {LOCAL_SERVER_URL} (Path is set to {MODEL_CHUNKING_PATH})")