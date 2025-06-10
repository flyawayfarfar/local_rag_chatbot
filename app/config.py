# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key:      str
    use_local_llm:       bool = False   # you already have this
    use_local_embeddings: bool = False  # ← new!
    data_dir: str = "data"
    local_embedding_model: str = "all-MiniLM-L6-v2"
    chroma_dir:          str = "chroma_db"
    k_neighbors:         int  = 5

    class Config:
        env_file = ".env"

settings = Settings()
