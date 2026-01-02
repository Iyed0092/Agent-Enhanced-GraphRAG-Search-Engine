# 🔗 Graph Augmented RAG

## 📝 Project Overview
This project implements a **Graph Augmented Retrieval-Augmented Generation (RAG)** system. It addresses the limitations of standard RAG by combining the semantic search capabilities of **Vector Databases** with the structural reasoning of **Knowledge Graphs (Neo4j)**.

While standard RAG is good at finding similar text, it often fails at "multi-hop" reasoning or understanding complex entity relationships (like dates, people, and hierarchies). Our solution uses a **Hybrid Router** to dynamically choose the best retrieval method for each user query.

## 🔒 Privacy & Local Hosting
We designed this system to be privacy-first.
* **Local Inference:** We use **Llama.cpp** and **LM Studio** to run quantized models locally.
* **Data Security:** No sensitive data is sent to external APIs during the ingestion or retrieval process.

## 📂 Project Structure

The codebase is modular, separating the decision logic (Router) from the model loading and settings.

```bash
📦 graph-augmented-rag
 ┣ 📂 app
 ┃ ┣ 📂 core
 ┃ ┃ ┣ 📜 settings.py       # Configuration (Paths, API Keys, URLs)
 ┃ ┃ ┗ 📜 llm_factory.py    # Factory to manage local GGUF models & clients
 ┃ ┣ 📜 router.py           # The "Brain": Decides between Vector, Graph, or Hybrid
 ┃ ┗ 📜 main.py             # Application entry point
 ┣ 📂 data                  # Raw documents and processed chunks
 ┣ 📂 models                # Directory for local GGUF model files
 ┗ 📜 requirements.txt      # Dependencies (langchain, neo4j, llama-cpp-python)
 ```

 ### Chunk 3: Model Architecture & Roles

```markdown
## Models & Roles

We utilize a "Swarm Architecture" where different specialized models handle specific tasks to optimize local performance.

| Component | Model Name / Source | Responsibility |
| :--- | :--- | :--- |
| **The Router** | **Qwen3-4B-Instruct** (Local GGUF) | Acts as the classifier. It analyzes the user query and outputs a JSON decision (`vector`, `graph`, or `both`) to direct the search path. |
| **Chunking Agent** | **LM Studio** (Local Server) | Connects to a local server instance (via LM Studio) to handle text cleaning and processing during the ingestion phase. |
| **The Reranker** | **Qwen3-4B-Instruct** (Local GGUF) | A local LLM instance that evaluates retrieved results from the graph and vector databases to prioritize the most relevant context. |
| **The Generator** | **Llama 3.3 70B Versatile** (Groq API) | Used for the final answer synthesis and code generation tasks to ensure high-speed and fluent responses. |
```

## ⚙️ Advanced Techniques

### 1. Hybrid Routing Strategy
Instead of sending every query to a vector database, we use an LLM-based router (`decide_tool`) to analyze the question:
* **Vector Path:** Selected for questions about definitions, specific articles, or unstructured content descriptions.
* **Graph Path:** Selected for questions about entities, relationships, or specific attributes (e.g., "Who signed X?", "What is connected to Y?").

### 2. Smart Chunking (Semantic & Context-Aware)
To improve retrieval accuracy, we moved beyond fixed-size chunking:
* **Semantic Chunking:** We measure cosine similarity between sentences. If the topic shifts, we start a new chunk, ensuring thematic consistency.
* **Context-Awareness:** We inject metadata (like document titles or section headers) into each chunk so that even small snippets retain their global context.

## 🕸️ Neo4j Knowledge Graph

We integrate **Neo4j** to handle structured relationships that standard vector search often misses. This allows the system to answer "multi-hop" questions by traversing connections between entities.

**Graph Schema:**
* **Nodes:** We extract specific entities such as `Person` (e.g., Ministers), `Organization` (e.g., Ministries), `Document` (e.g., Decrees), `Date`, and `Location`.
* **Relationships:** We define directed edges to capture how these entities interact, for example:
    * `(:Person)-[:SIGNED]->(:Document)`
    * `(:Ministry)-[:RELATED_TO]->(:Document)`
    * `(:Document)-[:PUBLISHED_ON]->(:Date)`

**Why Graph?**
While vector search finds "similar text," the graph allows us to find exact factual connections. For a query like *"Who signed the decree on January 5th?"*, the system traverses the graph from the `Date` node to the `Document` node and finally to the `Person` node to return the precise answer.
