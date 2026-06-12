from pydantic import BaseModel


class RankingResponse(BaseModel):
    id: int
    resume_id: int
    score: float
    justification: str | None = None
    name: str | None = None
    top_skills: str | None = None
    years_experience: int = 0 

    class Config:
        from_attributes = True