# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Switches
    use_local_llm:         bool = True           # default to local LLM (Ollama)
    use_local_embeddings:  bool = True           # default to local embeddings

    # Data / Vector DB
    data_dir:              str  = "data"
    chroma_dir:            str  = "chroma_db"
    k_neighbors:           int  = 5

    # Ollama
    ollama_base_url:       str  = "http://localhost:11434"
    ollama_model:          str  = "llama3.1:8b"
    ollama_embed_model:    str  = "nomic-embed-text"   # good local embedder

    # (optional) OpenAI fallback
    openai_api_key:        str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
