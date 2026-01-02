from app.core.llm_factory import ask_llm

def get_cypher_query(user_question, graph_schema):
    sys_msg = "You are a Neo4j expert. Write a Cypher query for the question. Return ONLY the code."
    
    prompt_text = f"Schema: {graph_schema}\nQuestion: {user_question}\nWrite the match query."

    response = ask_llm("coder", prompt_text, system=sys_msg)

    if response and "```" in response:
        response = response.replace("```cypher", "").replace("```", "")
    
    return response.strip()