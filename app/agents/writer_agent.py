from app.core.llm_factory import ask_llm

def generate_answer(query, context_data):
    if not context_data or len(context_data.strip()) < 10:
        return "Je ne trouve pas cette information dans les documents fournis. Veuillez reformuler ou vérifier si le sujet est traité dans la base."

    sys = """You are a rigorous AI assistant designed to answer questions based ONLY on the provided legal documents (JORT).

    STRICT RULES:
    1. NO OUTSIDE KNOWLEDGE: Ignore everything you know about the world. Use ONLY the information in the 'Context Information' block.
    2. NO HALLUCINATIONS: If the answer is not explicitly stated in the context, say "The provided text does not contain this information." Do NOT make up general rules or say "Generally...".
    3. BE PRECISE: If the user asks if 'X' is allowed, and the text only mentions 'Y', state clearly that the text ONLY mentions 'Y'.
    4. CITE SOURCES: Mention the Article numbers or Decree names if they appear in the context.
    """
    prompt = f"""
    ### CONTEXT INFORMATION (Source of Truth):
    {context_data}
    
    --------------------------------------------------
    
    ### USER QUESTION:
    {query}
    
    ### ANSWER (Based STRICTLY on the context above):
    """
    
    res = ask_llm("writer", prompt, system=sys)
    return res