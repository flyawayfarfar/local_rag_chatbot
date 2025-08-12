#

# My python 3.10.6
# pip: 23.3.2

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
	
