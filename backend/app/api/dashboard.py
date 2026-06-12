from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.job import Job
from app.models.resume import Resume

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def dashboard(
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).all()

    result = []

    for job in jobs:
        count = (
            db.query(Resume)
            .filter(
                Resume.job_id == job.id
            )
            .count()
        )

        result.append(
            {
                "id": job.id,
                "title": job.title,
                "resume_count": count
            }
        )

    return result