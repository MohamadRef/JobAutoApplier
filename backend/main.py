from fastapi import FastAPI, Query
from backend.jobs import search_jobs
from backend.database import init_db, save_jobs, get_saved_jobs

app = FastAPI(title="JobAutoApplier")

init_db()


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
def list_jobs(
    keyword: str = "",
    location: str = "Canada"
):
    jobs, errors = search_jobs(keyword, location)

    save_jobs(jobs)

    return {
        "total": len(jobs),
        "jobs": jobs,
        "errors": errors
    }


@app.get("/jobs/saved")
def saved_jobs():
    jobs = get_saved_jobs()

    return {
        "total": len(jobs),
        "jobs": jobs
    }