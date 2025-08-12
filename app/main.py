# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.config import settings

from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# Embeddings (must match what was used to build the index)
if settings.use_local_embeddings:
    from langchain_community.embeddings import OllamaEmbeddings
    EMBEDDINGS = OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url
    )
else:
    from langchain_community.embeddings import OpenAIEmbeddings
    EMBEDDINGS = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)

# LLM (Ollama vs OpenAI)
if settings.use_local_llm:
    from langchain_community.llms import Ollama
    LLM = Ollama(model=settings.ollama_model, base_url=settings.ollama_base_url, temperature=0.1)
else:
    from langchain_community.llms import OpenAI
    LLM = OpenAI(temperature=0.1)

class ChatRequest(BaseModel):
    query: str
    k: int | None = None

def make_chain(k_neighbors: int) -> RetrievalQA:
    db = Chroma(
        persist_directory=settings.chroma_dir,
        embedding_function=EMBEDDINGS,
        collection_name="local-rag"
    )
    retriever = db.as_retriever(search_kwargs={"k": k_neighbors})
    qa = RetrievalQA.from_chain_type(
        llm=LLM,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True  # helpful for debugging/citations
    )
    return qa

app = FastAPI(title="Local RAG (Ollama + Chroma)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Build chain once at startup
@app.on_event("startup")
def _startup():
    app.state.qa = make_chain(settings.k_neighbors)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        k = req.k or settings.k_neighbors
        # Adjust retriever K per-request when needed
        if k != settings.k_neighbors:
            app.state.qa = make_chain(k)

        result = app.state.qa.invoke({"query": req.query})
        # Format sources as a list of file paths
        sources = []
        for d in result.get("source_documents", []):
            src = d.metadata.get("source", "unknown")
            if src not in sources:
                sources.append(src)
        return {
            "answer": result.get("result", "").strip(),
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
