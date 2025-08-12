
# My python 3.10.6
# pip: 23.3.2

- Download ollama 
	- Install ollama
	- run the following to download ollama3.1
		ollama pull llama3.1:8b
		ollama pull nomic-embed-text

	- For light version 
		ollama pull llama3.1:8b-instruct-q4_K_M

- Install stuff for UI
	npm i framer-motion lucide-react
	npx shadcn@latest add button card input textarea badge tabs select tooltip sidebar


- Setup
	cd C:\dev\github\local_rag_chatbot
	python -m venv venv
	venv\Scripts\Activate
	pip install -r requirements.txt
	python -m app.build_index
	
	# Sync the requirements.txt and uninstall un necessary libs 
	pip install pip-tools   # if you haven’t already
	pip-sync requirements.txt
	pip install -r requirements.txt
	
	# Run the server 
	uvicorn app.main:app --reload

	# Test health 
	curl http://127.0.0.1:8000/health
	# should get: {"status":"ok"}

	# Test chat 
	curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"query\":\"What Project Alpha?\"}"
	# {"answer":" RAG stands for \"Retrieval-Augmented Generation\" and is a technique used in natural language processing to generate text responses based on retrieved information. It is often used in chatbots and other AI systems."}
	

- To switch from one to the other with the same db folder (local ollama vs openai api)
	- Update .env and update the following values
		USE_LOCAL_LLM=false
		USE_LOCAL_EMBEDDINGS=false
	- Delete the old db
		rm -rf chroma_db/
	- Run indexing
		python -m app.build_index
	- Start server
		uvicorn app.main:app --reload

- Now we use diff db folder for local ollama and api, then to switch one to the other:
	- Update .env and update the following values (true or false)
		USE_LOCAL_LLM=false
		USE_LOCAL_EMBEDDINGS=false
	- Run the following depends the value above
		# Build Ollama index
		set USE_LOCAL_EMBEDDINGS=true
		python -m app.build_index

		# Build OpenAI index
		set USE_LOCAL_EMBEDDINGS=false
		python -m app.build_index	