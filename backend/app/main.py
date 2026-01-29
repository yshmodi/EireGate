from fastapi import FastAPI

from app.api.v1.resume import router as resume_router

app = FastAPI(title="EireGate API", version="0.1.0")

app.include_router(resume_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict:
	return {"status": "ok"}
