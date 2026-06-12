import os
import chromadb
from app.core.config import CHROMA_PATH

os.makedirs(CHROMA_PATH, exist_ok=True)
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="resumes")
print(f"ChromaDB collection 'resumes' contains {collection.count()} embeddings")