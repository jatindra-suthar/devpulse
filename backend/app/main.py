from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api import repos, digests

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DevPulse API",
    description="AI-powered GitHub activity digest agent",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repos.router, prefix="/api")
app.include_router(digests.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
