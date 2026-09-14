import os
from dotenv import load_dotenv
import ollama

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "4"))

_client = None


def get_client() -> ollama.Client:
    global _client
    if _client is None:
        _client = ollama.Client(host=OLLAMA_BASE_URL, timeout=OLLAMA_TIMEOUT)
    return _client


def get_model() -> str:
    modelo = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    if not modelo:
        modelo = "llama3.2:3b"
    return modelo
