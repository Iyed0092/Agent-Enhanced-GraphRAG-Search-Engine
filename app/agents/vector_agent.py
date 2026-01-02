import json
from app.core.llm_factory import ask_llm

def rerank_documents(query, docs, top_k=5):
    if not docs:
        return []

    candidates_text = ""
    for i, d in enumerate(docs):
        snippet = d.page_content[:300].replace("\n", " ")
        candidates_text += f"ID {i}: {snippet}...\n\n"

    sys = "You are an expert Search Ranker. Your goal is to select the most relevant documents for a query."
    
    prompt = f"""
    USER QUERY: "{query}"

    CANDIDATE DOCUMENTS:
    {candidates_text}

    INSTRUCTIONS:
    1. Analyze the relevance of each document ID to the query.
    2. Select the top {top_k} most relevant documents.
    3. Return ONLY a JSON list of the selected IDs, sorted by relevance (best first).
    4. Example output: [2, 0, 4]
    
    JSON Output:
    """

    res = ask_llm("reranker", prompt, system=sys)
    best_docs = []
    clean_res = res.strip().replace("```json", "").replace("```", "")
    start = clean_res.find("[")
    end = clean_res.rfind("]") + 1
    
    if start != -1 and end != -1:
        indices = json.loads(clean_res[start:end])
        for idx in indices:
            if isinstance(idx, int) and 0 <= idx < len(docs):
                best_docs.append(docs[idx])
    else:
        print("Reranker returned invalid format. Keeping original order.")
        return docs[:top_k]

    if not best_docs:
        return docs[:1]

    return best_docs