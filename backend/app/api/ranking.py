from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.core.db import get_db
from app.models.resume import Resume
from app.services.ranking_service import rank_candidates
from app.core.chroma import collection

router = APIRouter(prefix="/rank", tags=["Ranking"])
logger = logging.getLogger(__name__)


@router.post("")
def rank(jd: str, db: Session = Depends(get_db)):
    resumes = db.query(Resume).filter(Resume.profile_json.isnot(None)).all()
    if not resumes:
        logger.info("No resumes with profile_json")
        return []

    resume_ids = [str(r.id) for r in resumes]
    logger.info(f"Querying ChromaDB for ids: {resume_ids}")

    try:
        # First try direct ID lookup
        chroma_result = collection.get(ids=resume_ids, include=["embeddings", "metadatas"])
        ids = chroma_result.get("ids") or []
        # Get embeddings – do NOT use `or []` directly if it might be an array
        embeddings_raw = chroma_result.get("embeddings")
        embeddings = embeddings_raw if embeddings_raw is not None else []

        # If no results, fall back to metadata query
        if not ids:
            logger.warning(f"ID lookup returned empty, trying metadata query for resume_ids={resume_ids}")
            int_ids = [int(rid) for rid in resume_ids]
            meta_result = collection.get(
                where={"resume_id": {"$in": int_ids}},
                include=["embeddings", "metadatas"]
            )
            ids = meta_result.get("ids") or []
            embeddings_raw = meta_result.get("embeddings")
            embeddings = embeddings_raw if embeddings_raw is not None else []
            chroma_result = meta_result
            logger.info(f"Metadata query returned {len(ids)} embeddings")

    except Exception as e:
        logger.error(f"Chroma get failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Embedding retrieval failed")

    logger.info(f"ChromaDB returned {len(ids)} embeddings (expected {len(resume_ids)})")

    if not ids:
        logger.warning(f"No embeddings found for resume ids: {resume_ids}")
        return []

    # Build mapping from ID string to embedding
    embedding_map = {}
    for i, rid in enumerate(ids):
        if i < len(embeddings):
            embedding_map[rid] = embeddings[i]

    resume_data = []
    for r in resumes:
        rid_str = str(r.id)
        emb = embedding_map.get(rid_str)

        # If not found by string ID, try to find via metadata
        if emb is None and chroma_result.get("metadatas"):
            for idx, meta in enumerate(chroma_result["metadatas"]):
                if meta and meta.get("resume_id") == r.id and idx < len(embeddings):
                    emb = embeddings[idx]
                    break

        if emb is None:
            logger.warning(f"Missing embedding for resume {r.id}")
            continue

        resume_data.append({
            "resume_id": r.id,
            "profile_text": r.profile_json,
            "years_experience": r.years_experience or 0,
            "embedding": emb,
            "top_skills": r.top_skills,
        })

    if not resume_data:
        return []

    results = rank_candidates(jd, resume_data)
    return results