import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from app.core import settings
from app.ingestion.chunking_strategy import semantic_chunking_with_context

def ingest_documents():
    pdf_folder = settings.DATA_PATH
    all_chunks = []
    embed_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if not os.path.exists(pdf_folder):
        print("No data folder found")
        return

    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            path = os.path.join(pdf_folder, file)
            print(f"Processing {file}...")
            
            loader = PyPDFLoader(path)
            pages = loader.load()

            for page in pages:
                raw_text = page.page_content
                enriched_chunks = semantic_chunking_with_context(raw_text)
                for chunk_text in enriched_chunks:
                    doc_obj = page.copy()
                    doc_obj.page_content = chunk_text
                    all_chunks.append(doc_obj)

    if len(all_chunks) > 0:
        print(f"Creating vector store with {len(all_chunks)} chunks...")
        vector_store = FAISS.from_documents(all_chunks, embed_model)
        vector_store.save_local(settings.VECTOR_INDEX_PATH)
        print("Saved FAISS index locally.")
    else:
        print("No documents were processed.")

if __name__ == "__main__":
    ingest_documents()