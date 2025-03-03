# Debate AI
Agentic AI research-paper debate / learning tool using LangChain, OpenAI, RAG and Vector Databases. Pits two LLMs against each other and manages a debate on a hot topic in the user uploaded research paper.

## Experiments
### 2.1-debate-setup-hugchat.ipynb
1. Receives uploaded research paper document, processes and stores it for RAG, and asks an LLM to provide debate topics with For and Against motions.
2. Sends the For motion to one AI Agent and the Against motion to another AI agent.
3. Manager AI Agent manages the debate, and stops it either when there's consensus or if a certain number of points hav been made by either side.
4. Summarizes and concludes the debate.

### 1.0-load-data-sm.ipynb
1. Processes uploaded Questions and Answers on Solar System.
2. Splits data into chunks and prepares embeddings for the data using my locally deployed Llama 3.2 model and embeddings.
3. Loads them into high-performance, production-ready **Weaviate** Vector database.
4. Performs search to find relevant stored documents for a prompt and uses Hugging Chat LLM for inference.

### 1.0-load-data-sm-faiss.ipynb
1. Processes uploaded Questions and Answers on Solar System.
2. Splits data into chunks and prepares embeddings for the data using my locally deployed Llama 3.2 model and embeddings.
3. Loads them into high-performance, **Facebook AI Similarity Search** Vector database.
4. Performs search to find relevant stored documents for a prompt and uses Hugging Chat LLM for inference.
5. Compares performance between Weaviate and FAISS.

### 1.3-RAG.ipynb
Performs similarity search on Weaviate persisted documents to find relevant stored documents for a prompt and uses Hugging Chat LLM for inference.

Full Retrieval Augemented Generation process on persisted data.

## References
1. What are Vector Databases? https://www.youtube.com/watch?v=ebMkbWzFCnA
2. LangChain for orchestrating all the steps: https://python.langchain.com/docs/tutorials/rag/#components
3. Weaviate https://python.langchain.com/docs/integrations/vectorstores/weaviate/#environment-setup
4. Weaviate Search https://weaviate.io/developers/weaviate/search/basics