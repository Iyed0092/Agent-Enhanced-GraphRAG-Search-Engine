from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.router_agent import decide_tool
from app.agents.graph_agent import get_cypher_query
from app.agents.writer_agent import generate_answer
from app.agents.vector_agent import rerank_documents
from app.tools.vector_tool import search_vector_db
from app.tools.graph_tool import run_cypher

router = APIRouter()

class QueryRequest(BaseModel):
    message: str

@router.post("/chat")
def chat_endpoint(req: QueryRequest):
    user_msg = req.message
    
    tool_choice = decide_tool(user_msg)
    
    context = ""
    
    if tool_choice == "vector" or tool_choice == "both":
        raw_docs = search_vector_db(user_msg)
        good_docs = rerank_documents(user_msg, raw_docs)
        for d in good_docs:
            context += d.page_content + "\n"

    if tool_choice == "graph" or tool_choice == "both":
        schema = "(:Page)-[:MENTIONS]->(:Entity)"
        cypher = get_cypher_query(user_msg, schema)
        graph_data = run_cypher(cypher)
        context += str(graph_data) + "\n"

    final_res = generate_answer(user_msg, context)
    
    return {"response": final_res, "tool_used": tool_choice}