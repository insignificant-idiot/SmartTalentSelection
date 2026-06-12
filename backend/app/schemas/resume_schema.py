from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: int
    file_name: str
    years_experience: int

    class Config:
        from_attributes = True