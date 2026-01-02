from neo4j import GraphDatabase
from app.core import settings

def run_cypher(query):
    driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
    
    data = []
    try:
        with driver.session() as session:
            result = session.run(query)
            for r in result:
                data.append(r.data())
    except Exception as e:
        print(e)
        
    driver.close()
    return data