import os
import gradio as gr
from ollama import Client as OllamaClient
from chromadb import HttpClient as ChromaHttpClient
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
CHROMA_HOST = os.getenv("CHROMA_HOST", "http://localhost:8000") # http://chroma:8000

def init_chroma_client():
    global chroma_client
    chroma_host, chroma_port = CHROMA_HOST.replace("http://", "").split(':', 1)
    chroma_client = ChromaHttpClient(
        host=chroma_host,
        port=chroma_port,
        ssl=False
    ) 
    chroma_client.heartbeat()
    return chroma_client

def init_embedding_function():
    global ollama_ef
    ollama_ef = OllamaEmbeddingFunction(
        url=OLLAMA_HOST,
        model_name=OLLAMA_EMBED_MODEL,
    )
    return ollama_ef

def init_ollama_client():
    global client
    client = OllamaClient(host=OLLAMA_HOST)
    return client

def chatter(query, history):
    # Original implementation: medium.com/@mbrazel/open-source-self-hosted-rag-llm-server-with-chromadb-docker-ollama-7e6c6913da7a
    def get_system_message_rag(content):
        return f"""You are an expert fantasy writer.

        Generate your response by following the steps below:
        1. Recursively break down the question into smaller questions.
        2. For each question/directive:
            2a. Select the most relevant information from the context in light of the conversation history.
        3. Generate a draft response using selected information.
        4. Remove duplicate content from draft response.
        5. Generate your final response after adjusting it to increase accuracy and relevance.
        6. Do not try to summarise the answers, explain it properly.
        6. Only show your final response! 
        
        Constraints:
        1. DO NOT PROVIDE ANY EXPLANATION OR DETAILS OR MENTION THAT YOU WERE GIVEN CONTEXT.
        2. Don't mention that you are not able to find the answer in the provided context.
        3. Don't make up the answers by yourself.
        4. Try your best to provide answer from the given context.

        CONTENT:
        {content}
        """

    def get_ques_response_prompt(question):
        return f"""
        ==============================================================
        Based on the above context, please provide the answer to the following question:
        {question}
        """

    def retrieve_context(query):
        query_embeddings = ollama_ef(query)
        return chroma_client.get_collection(name="notes") \
            .query(query_embeddings=query_embeddings, include=["documents"])

    def generate_rag_response(content, question):
        stream = client.chat(model=OLLAMA_MODEL, messages=[
            {"role": "system", "content": get_system_message_rag(content)},            
            {"role": "user", "content": get_ques_response_prompt(question)}
            ], stream=True
        )
        full_answer = ''
        for chunk in stream:
            full_answer =''.join([full_answer,chunk['message']['content']])
        return full_answer

    return generate_rag_response(retrieve_context(query), query)

def main():
    init_chroma_client()
    init_embedding_function()
    init_ollama_client()

    chat = gr.ChatInterface(fn=chatter,
        examples=["Who is Adapa?"],
        title="My Chatbot"
    )
    chat.launch()

if __name__ == "__main__":
    main()
