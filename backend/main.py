from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.jobs import search_jobs
from backend.database import init_db, save_jobs, get_saved_jobs
from backend.matcher import rank_jobs
from backend.resume import save_resume, get_resume_text

app = FastAPI(title="JobAutoApplier")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

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


@app.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    return await save_resume(file)


@app.get("/resume/status")
def resume_status():
    resume_text = get_resume_text()

    return {
        "uploaded": bool(resume_text.strip()),
        "characters": len(resume_text)
    }


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


@app.get("/jobs/matched")
def matched_jobs(
    keyword: str = "",
    location: str = "Canada"
):
    jobs, errors = search_jobs(keyword, location)
    save_jobs(jobs)

    ranked_jobs = rank_jobs(jobs)

    return {
        "total": len(ranked_jobs),
        "jobs": ranked_jobs,
        "errors": errors
    }