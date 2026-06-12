from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime

from datetime import datetime, timezone

from app.core.db import Base


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    file_name = Column(String, nullable=False)
    batch_name = Column(String, nullable=True)
    raw_text = Column(Text)
    profile_json = Column(Text)
    years_experience = Column(Integer, default=0)
    top_skills = Column(Text)
    embedding_id = Column(String)
    processing_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))