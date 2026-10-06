import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Default event as_of_date is 2026-10-06 as specified in Addendum v2
DEFAULT_AS_OF_DATE = os.environ.get("AS_OF_DATE", "2026-10-06")

# Database & Vector DB paths
CHROMA_PATH = os.environ.get("CHROMA_PATH", "./data/chroma_db")
SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "./data/university.db")

# Ollama & LLM API Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3:latest")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
CLOUD_FALLBACK = os.environ.get("CLOUD_FALLBACK", "false").lower() == "true"
AUTO_RULE_EXTRACTION = os.environ.get("AUTO_RULE_EXTRACTION", "false").lower() == "true"

# Top K vector hits
TOP_K = int(os.environ.get("TOP_K", "4"))
