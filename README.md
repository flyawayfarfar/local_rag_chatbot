# Local RAG Chatbot

**Python:** 3.10.6  
**pip:** 23.3.2

---

## Setup Instructions

1. **Download and install Ollama**  
   Follow instructions from [Ollama’s official site](https://ollama.com/).

2. **Download models**

   **Full version:**
   ```bash
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

   **Light version:**
   ```bash
   ollama pull llama3.1:8b-instruct-q4_K_M
   ```

3. **Setup Python environment**
   ```bash
   cd C:\dev\github\local_rag_chatbot
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Sync the `requirements.txt` and uninstall unnecessary libraries**
   ```bash
   pip install pip-tools   # if you haven’t already
   pip-sync requirements.txt
   pip install -r requirements.txt
   ```

5. **Build the index**
   ```bash
   python -m app.build_index
   ```

6. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Test the health endpoint**
   ```bash
   curl http://127.0.0.1:8000/health
   # should get: {"status":"ok"}
   ```

8. **Test chat**
   ```bash
   curl -X POST http://127.0.0.1:8000/chat      -H "Content-Type: application/json"      -d "{\"query\":\"What Project Alpha?\"}"
   # Example:
   # {"answer":"RAG stands for \"Retrieval-Augmented Generation\" and is a technique used in natural language processing to generate text responses based on retrieved information. It is often used in chatbots and other AI systems."}
   ```

---

## Switching Between Local Ollama and API

We use different database folders for local Ollama and API modes, so switching does not require re-indexing.

1. Update `.env` and set:
   ```env
   USE_LOCAL_LLM=false
   USE_LOCAL_EMBEDDINGS=false
   ```

2. Build index based on mode:

   **For Ollama index:**
   ```bash
   set USE_LOCAL_EMBEDDINGS=true
   python -m app.build_index
   ```

   **For OpenAI index:**
   ```bash
   set USE_LOCAL_EMBEDDINGS=false
   python -m app.build_index
   ```
