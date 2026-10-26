from fastapi import FastAPI
from backend.jobs import get_jobs

app = FastAPI(title="JobAutoApplier")


@app.get("/")
def home():
    return {
        "message": "JobAutoApplier API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/jobs")
def list_jobs():
    return {"jobs": get_jobs()}