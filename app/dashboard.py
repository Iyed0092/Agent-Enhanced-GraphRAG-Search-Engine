import streamlit as st
import requests
import os
import subprocess

API_URL = "http://localhost:8000/chat"
DATA_FOLDER = "data/raw_docs"

os.makedirs(DATA_FOLDER, exist_ok=True)

st.set_page_config(page_title="Hybrid RAG Engine", layout="wide")

st.title("🧠 Hybrid Graph RAG Engine")
st.caption("Powered by Local LLM (Qwen/Mistral) + Neo4j + FAISS")

with st.sidebar:
    st.header("📂 Gestion des Documents")
    
    uploaded_file = st.file_uploader("Ajouter un PDF", type=["pdf"])
    
    if uploaded_file is not None:
        file_path = os.path.join(DATA_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Fichier '{uploaded_file.name}' sauvegardé !")

    st.divider()

    if st.button("🔄 Mettre à jour la Base (Ingest)"):
        with st.status("Traitement en cours...", expanded=True) as status:
            st.write("📚 Construction de l'index Vectoriel (FAISS)...")
            subprocess.run(["python", "-m", "app.ingestion.build_vector"], check=True)
            st.write("✅ Vecteurs indexés.")


            st.write("🕸️ Construction du Graphe (Neo4j)...")
            subprocess.run(["python", "-m", "app.ingestion.build_graph"], check=True)
            st.write("✅ Graphe construit.")
            status.update(label="Base de connaissances à jour !", state="complete")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Posez votre question sur les documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Analyse en cours (Router -> Search -> LLM)..."):
            try:
                res = requests.post(API_URL, json={"message": prompt})
                
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("response", "Pas de réponse.")
                    tool = data.get("tool_used", "unknown")
                    full_response = answer
                    st.markdown(full_response)
                    st.caption(f"🛠️ Outil utilisé : **{tool.upper()}**")
                else:
                    st.error(f"Erreur API: {res.status_code}")
            except Exception as e:
                st.error(f"Erreur de connexion : {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})