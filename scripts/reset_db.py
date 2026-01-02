import os
import shutil
from neo4j import GraphDatabase
from app.core import settings

def clear_vector_db():
    print("Deleting Vector Index...")
    index_path = settings.VECTOR_INDEX_PATH
    
    # FAISS usually creates a folder or a file depending on how you save
    # In our code we saved as a local index folder
    if os.path.exists(index_path):
        try:
            if os.path.isdir(index_path):
                shutil.rmtree(index_path)
            else:
                os.remove(index_path)
            print("✅ FAISS index deleted.")
        except Exception as e:
            print(f"❌ Error deleting FAISS: {e}")
    else:
        print("⚠️ No FAISS index found.")

def clear_graph_db():
    print("Clearing Neo4j Database...")
    driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
    
    try:
        with driver.session() as session:
            # detach delete wipes all nodes and relationships
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Graph database wiped.")
    except Exception as e:
        print(f"❌ Error clearing Graph: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete ALL data? (yes/no): ")
    if confirm.lower() == "yes":
        clear_vector_db()
        clear_graph_db()
        print("System is clean. Ready to re-ingest.")
    else:
        print("Operation cancelled.")