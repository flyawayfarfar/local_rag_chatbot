# app/rag_pipeline.py
import os
from typing import List
from app.config import settings

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Loaders
from langchain_community.document_loaders import (
    DirectoryLoader, PyPDFLoader, TextLoader
)

# Embeddings
if settings.use_local_embeddings:
    # Use Ollama embeddings for full-local stack
    from langchain_community.embeddings import OllamaEmbeddings
    def make_embedder():
        return OllamaEmbeddings(
            model=settings.ollama_embed_model,
            base_url=settings.ollama_base_url
        )
else:
    # Fallback to OpenAI if desired
    from langchain_community.embeddings import OpenAIEmbeddings
    def make_embedder():
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        return OpenAIEmbeddings(openai_api_key=settings.openai_api_key)

def load_documents(data_dir: str) -> List[Document]:
    docs: List[Document] = []

    # PDFs
    try:
        pdf_loader = DirectoryLoader(
            data_dir, glob="**/*.pdf", loader_cls=PyPDFLoader, recursive=True
        )
        docs.extend(pdf_loader.load())
    except Exception as e:
        print("PDF load error:", e)

    # Plain text / markdown / csv as text
    for pattern in ("**/*.txt", "**/*.md", "**/*.csv"):
        try:
            loader = DirectoryLoader(
                data_dir, glob=pattern, loader_cls=TextLoader, recursive=True
            )
            docs.extend(loader.load())
        except Exception as e:
            print(f"Load error for {pattern}:", e)

    # If no loaders matched, try the simplest fallback (files in root)
    if not docs and os.path.isdir(data_dir):
        for fname in os.listdir(data_dir):
            fpath = os.path.join(data_dir, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        docs.append(Document(page_content=f.read(), metadata={"source": fpath}))
                except Exception as e:
                    print("Fallback read error:", fpath, e)

    return docs

def chunk_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900, chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_documents(docs)

def build_vector_store() -> Chroma:
    docs = load_documents(settings.data_dir)
    if not docs:
        print("No documents found in", settings.data_dir)
        raise SystemExit(0)

    chunks = chunk_documents(docs)
    print(f"Loaded {len(docs)} docs → {len(chunks)} chunks")

    embeddings = make_embedder()
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.chroma_dir,
        collection_name="local-rag"
    )
    vectordb.persist()
    return vectordb
