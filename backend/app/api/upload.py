import os
import uuid
import json
import logging

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.resume import Resume
from app.services.parser_service import extract_text
from app.services.groq_service import extract_profile
from app.services.embedding_service import save_resume_embedding

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {".pdf", ".docx", ".jpg", ".jpeg", ".png"}


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    job_id: int = Form(None),
    db: Session = Depends(get_db)
):
    extension = os.path.splitext(file.filename)[1].lower() # type: ignore
    if extension not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    unique_name = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        text = extract_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    resume = Resume(
        file_name=file.filename,
        raw_text=text,
        job_id=job_id
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    try:
        profile = extract_profile(text)
        resume.profile_json = json.dumps(profile) # type: ignore
        resume.years_experience = profile.get("years_experience", 0)
        skills = profile.get("skills", [])
        resume.top_skills = ", ".join(skills[:5]) if skills else None # type: ignore

        # Save embedding and verify
        embedding_id = save_resume_embedding(resume.id, text, resume.years_experience)
        resume.embedding_id = embedding_id # type: ignore
        resume.processing_status = "completed" # type: ignore
        logger.info(f"Resume {resume.id} processed successfully")
    except Exception as e:
        resume.processing_status = f"failed: {str(e)}" # type: ignore
        logger.error(f"Resume {resume.id} processing failed: {e}", exc_info=True)

    db.commit()
    db.refresh(resume)

    return {
        "resume_id": resume.id,
        "file_name": resume.file_name,
        "characters": len(text),
        "processing_status": resume.processing_status
    }


@router.get("/resumes")
def get_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).all()
    return resumes