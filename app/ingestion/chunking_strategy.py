from app.core.llm_factory import ask_llm

def semantic_chunking_with_context(raw_text):
    prompt_text = f"""
    Analyze the following text from a document.
    Task 1: Split it into semantically complete chunks (group related sentences together).
    Task 2: For each chunk, prepend a short context description in brackets [Context].
    
    Example Output:
    [Introduction to Liability] The liability of the company is limited to...
    |||
    [Exceptions to Warranty] However, this warranty does not apply if...

    Here is the text to process:
    {raw_text}
    """
    res = ask_llm(
        role="chunking",
        prompt=prompt_text,
        system="You are a data processing assistant. Split text semantically and enrich with context."
    )

    if res:
        final_chunks = []
        raw_splits = res.split("|||")
        
        for part in raw_splits:
            cleaned = part.strip()
            if len(cleaned) > 20: 
                final_chunks.append(cleaned)
        
        if len(final_chunks) > 0:
            return final_chunks
    
    return [raw_text]