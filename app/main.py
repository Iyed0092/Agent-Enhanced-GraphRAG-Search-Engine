import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core import settings
from app.core.llm_factory import load_file_model as load_local_model
from app.api.routes import router as api_router 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🚀 INITIALIZATION: Pre-loading Qwen Model into GPU...")
    
    if settings.MODEL_ROUTER_PATH:
        load_local_model(settings.MODEL_ROUTER_PATH)
        print("✅ Qwen Model loaded and ready in VRAM!")

    yield
    
    print("🛑 Shutting down and clearing VRAM...")

app = FastAPI(
    title="Hybrid Graph RAG Engine",
    version="1.0",
    lifespan=lifespan 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)