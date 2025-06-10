# app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# community imports
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import OpenAI

# core chain stays in langchain
from langchain.chains import RetrievalQA

from app.config import settings

app = FastAPI(title="On-Prem RAG Chatbot")

# (optional) allow CORS for browser demos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

@app.on_event("startup")
def load_resources():
    # config
    api_key     = settings.openai_api_key
    chroma_dir  = settings.chroma_dir
    k_neighbors = settings.k_neighbors

    # embeddings & vector store
    embed_model  = OpenAIEmbeddings(openai_api_key=api_key)
    vector_store = Chroma(
        persist_directory=chroma_dir,
        embedding_function=embed_model,
    )

    # LLM (you can swap to a local model via your factory)
    llm = OpenAI(openai_api_key=api_key, temperature=0.2)

    # RetrievalQA chain
    retriever = vector_store.as_retriever(search_kwargs={"k": k_neighbors})
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
    )

    app.state.qa = qa

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        answer = await app.state.qa.arun(req.query)
        return {"answer": answer}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")
