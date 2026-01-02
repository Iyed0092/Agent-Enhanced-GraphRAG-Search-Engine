import json
from app.core.llm_factory import ask_llm

def decide_tool(user_query):
    sys = "You are an expert Query Router. Your job is to direct the user's question to the best database."

    prompt = f"""
    Analyze the user question and select the best tool:
    
    1. 'vector': Use for questions about CONTENT, DEFINITIONS, ARTICLES, or LAWS.
       - Examples: "What does Article 11 say?", "How to change university?", "Summary of the decree."
       
    2. 'graph': Use for questions about ENTITIES, RELATIONS, PEOPLE, or DATES.
       - Examples: "Who signed the decree?", "Which ministries are linked to the petrol sector?", "What decrees involve Malek Zahi?"
       
    3. 'both': Use ONLY if the question requires finding a specific text AND connecting it to entities.
       - Examples: "What are the conditions in the decree signed by Najla Bouden?"

    Question: "{user_query}"
    
    Return ONLY a JSON object: {{"tool": "value"}}
    """

    res = ask_llm("router", prompt, system=sys)

    clean_res = res.strip().replace("```json", "").replace("```", "")
    start = clean_res.find("{")
    end = clean_res.rfind("}") + 1
    
    if start != -1 and end != -1:
        json_str = clean_res[start:end]
        data = json.loads(json_str)
        tool = data.get("tool", "both").lower()
        
        if tool not in ["vector", "graph", "both"]:
            return "both"
        return tool
    else:
        return "both"
            