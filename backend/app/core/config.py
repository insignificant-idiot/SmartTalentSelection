from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./talent.db")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")

LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:12434")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M")