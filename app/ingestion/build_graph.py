import os
import json
import re
from langchain_community.document_loaders import PyPDFLoader
from neo4j import GraphDatabase
from app.core import settings
from app.core.llm_factory import ask_llm
from app.ingestion.chunking_strategy import semantic_chunking_with_context

def extract_triplets(text_chunk):
    sys = """You are an expert Knowledge Graph Extractor.
    Your task is to identify entities (Subject, Object) and the relationships between them in the provided text.

    Rules:
    1. Extract meaningful relationships based on the context.
    2. Relations must be verbs or prepositions in UPPER_CASE (e.g., LOCATED_IN, MENTIONS, DEFINES, IS_A, SIGNED_BY).
    3. Entities must be precise (e.g., "Google" instead of "Company").
    4. Return ONLY a valid JSON list of objects. No markdown, no explanations.
    5. Format: [{"head": "SourceEntity", "relation": "RELATION_TYPE", "tail": "TargetEntity"}]
    """
    
    prompt = f"Analyze this text and extract the graph:\n---\n{text_chunk}\n---\nJSON Output:"
    res = ask_llm("extraction", prompt, system=sys)
    start = res.find("[")
    end = res.rfind("]") + 1
    json_str = res[start:end]
    return json.loads(json_str)


def push_to_neo4j(driver, triplets):
    with driver.session() as session:
        for t in triplets:
            raw_rel = t.get('relation', 'RELATED_TO')
            clean_rel = re.sub(r'[^a-zA-Z0-9]', '_', raw_rel).upper()
            clean_rel = re.sub(r'_+', '_', clean_rel).strip('_')
            if not clean_rel: clean_rel = "RELATED_TO"
            cypher = f"""
            MERGE (h:Entity {{name: $head}})
            MERGE (t:Entity {{name: $tail}})
            MERGE (h)-[:{clean_rel}]->(t)
            """ 
            session.run(cypher, head=t['head'], tail=t['tail'])

def clear_graph(driver):
    print("Cleaning old Graph data...")
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

def build_graph():
    folder = settings.DATA_PATH
    if not os.path.exists(folder):
        return

    driver = GraphDatabase.driver(
        settings.NEO4J_URI, 
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )

    try:
        clear_graph(driver)

        for file in os.listdir(folder):
            if file.endswith(".pdf"):
                path = os.path.join(folder, file)
                print(f"Processing {file}...")
                
                loader = PyPDFLoader(path)
                pages = loader.load()

                for page in pages:
                    chunks = semantic_chunking_with_context(page.page_content)
                    
                    for i, c in enumerate(chunks):
                        data = extract_triplets(c)
                        
                        if data:
                            push_to_neo4j(driver, data)
                            print(f"   -> Chunk {i+1}: Added {len(data)} relations.")
                            
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        driver.close()
        print("Neo4j connection closed.")

if __name__ == "__main__":
    build_graph()