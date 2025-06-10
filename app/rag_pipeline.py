# app/rag_pipeline.py

import os
from app.config import settings
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma

# only import the SentenceTransformer wrapper if you actually need local embeddings
if settings.use_local_embeddings:
    from langchain_community.embeddings import HuggingFaceEmbeddings
else:
    from langchain_community.embeddings import OpenAIEmbeddings

def load_documents(data_dir: str) -> list[Document]:
    docs = []
    for fname in os.listdir(data_dir):
        if fname.lower().endswith((".txt", ".md")):
            with open(os.path.join(data_dir, fname), encoding="utf-8") as f:
                text = f.read()
            docs.append(Document(page_content=text, metadata={"source": fname}))
    return docs

def build_vector_store():
    """
    Build & persist a Chroma index, using either OpenAI or local SBERT embeddings.
    """
    docs = load_documents(settings.data_dir)

    if settings.use_local_embeddings:
        # wrap your SentenceTransformer with LangChain’s HuggingFaceEmbeddings
        embedder = HuggingFaceEmbeddings(
            model_name=settings.local_embedding_model
        )
    else:
        embedder = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key
        )

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embedder,                 # pass the Embeddings object, not a bare function
        persist_directory=settings.chroma_dir,
    )
    vectordb.persist()
    return vectordb
