from fastapi import APIRouter
from app.core.chroma import collection

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/embeddings")
def list_embeddings():
    result = collection.get()
    return {
        "count": len(result.get("ids", [])),
        "ids": result.get("ids", []),
        "metadatas": result.get("metadatas", [])
    }