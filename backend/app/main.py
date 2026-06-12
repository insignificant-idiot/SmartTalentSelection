from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import Base
from app.core.db import engine

from app.models.job import Job
from app.models.resume import Resume
from app.models.ranking import Ranking

from app.api.jobs import router as jobs_router
from app.api.dashboard import router as dashboard_router
from app.api.upload import router as upload_router
from app.api.ranking import router as ranking_router
from app.api.debug import router as debug_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Talent Selection Engine", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(jobs_router)
app.include_router(dashboard_router)
app.include_router(upload_router)
app.include_router(ranking_router)
app.include_router(debug_router)

@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "smart-talent-engine"
    }