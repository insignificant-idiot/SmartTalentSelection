import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.chroma import collection

logger = logging.getLogger(__name__)
model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embedding(text):
    return model.encode(text).tolist()

def save_resume_embedding(resume_id, profile_text, years_experience):
    """Save embedding to ChromaDB and verify it was stored."""
    try:
        embedding = create_embedding(profile_text)
        if any(not np.isfinite(x) for x in embedding):
            raise ValueError("Embedding contains NaN or Inf")

        resume_id_str = str(resume_id).strip()
        collection.add(
            ids=[resume_id_str],
            documents=[profile_text],
            embeddings=[embedding],
            metadatas=[{"resume_id": resume_id, "years_experience": years_experience}]
        )
        logger.info(f"Added embedding for resume {resume_id} to ChromaDB with id '{resume_id_str}'")

        # Verify by ID
        result = collection.get(ids=[resume_id_str], include=["embeddings"])
        if result and result.get("ids"):
            logger.info(f"Verified embedding for resume {resume_id} (id='{result['ids'][0]}')")
            return resume_id_str
        else:
            # Try verification by metadata
            meta_result = collection.get(where={"resume_id": resume_id}, include=["embeddings"])
            if meta_result.get("ids"):
                logger.info(f"Verified embedding via metadata for resume {resume_id}")
                return resume_id_str
            else:
                logger.error(f"Verification failed for resume {resume_id}: {result}")
                raise RuntimeError("Embedding not found after add")

    except Exception as e:
        logger.error(f"Error saving embedding for resume {resume_id}: {e}", exc_info=True)
        raise