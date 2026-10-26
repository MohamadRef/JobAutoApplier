from fastapi import FastAPI
from backend.jobs import get_jobs, get_himalayas_jobs

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
    remotive_jobs = get_jobs()
    himalayas_jobs = get_himalayas_jobs()

    return {
        "total": len(remotive_jobs) + len(himalayas_jobs),
        "jobs": remotive_jobs + himalayas_jobs
    }