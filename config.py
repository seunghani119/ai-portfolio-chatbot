import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings

load_dotenv()

CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "bge-m3")
OWNER_NAME = os.getenv("OWNER_NAME", "승한")

DATA_DIR = "data"
DB_DIR = "chroma_db"
COLLECTION_NAME = "portfolio"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 6


def get_embeddings():
    return OllamaEmbeddings(model=EMBED_MODEL)


def get_llm():
    return ChatOllama(model=CHAT_MODEL, temperature=0, num_ctx=8192)