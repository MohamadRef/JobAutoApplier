from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.jobs import search_jobs
from backend.database import init_db, save_jobs, get_saved_jobs
from backend.matcher import rank_jobs
from backend.resume import save_resume, get_resume_text
from backend.tracking import init_tracking, list_tracking, update_tracking, STATUSES
from backend.eligibility import review_eligibility
from backend.applications import prepare_application

app = FastAPI(title='JobAutoApplier')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)
init_db()
init_tracking()


class ApplicationPrepareRequest(BaseModel):
    job: dict


class TrackingUpdate(BaseModel):
    source: str = Field(min_length=1)
    job_id: str = Field(min_length=1)
    saved: bool = False
    status: str = 'Not Applied'
    job: dict = Field(default_factory=dict)


@app.get('/')
def home():
    return {'message': 'JobAutoApplier API is running', 'status': 'success'}


@app.get('/health')
def health():
    return {'status': 'healthy'}


@app.post('/resume/upload')
async def upload_resume(file: UploadFile = File(...)):
    return await save_resume(file)


@app.get('/resume/status')
def resume_status():
    content = get_resume_text()
    return {'uploaded': bool(content.strip()), 'characters': len(content)}


@app.get('/jobs')
def list_jobs(keyword: str = '', location: str = 'Canada'):
    jobs, errors = search_jobs(keyword, location)
    save_jobs(jobs)
    return {'total': len(jobs), 'jobs': jobs, 'errors': errors}


@app.get('/jobs/saved')
def saved_jobs():
    jobs = get_saved_jobs()
    return {'total': len(jobs), 'jobs': jobs}


@app.get('/jobs/matched')
def matched_jobs(keyword: str = '', location: str = 'Canada'):
    jobs, errors = search_jobs(keyword, location)
    save_jobs(jobs)
    ranked_jobs = rank_jobs(jobs)
    for job in ranked_jobs:
        job.update(review_eligibility(job))
    return {'total': len(ranked_jobs), 'jobs': ranked_jobs, 'errors': errors}


@app.get('/tracking')
def tracked_jobs():
    return {'items': list_tracking(), 'statuses': sorted(STATUSES)}


@app.post('/tracking')
def track_job(payload: TrackingUpdate):
    if payload.status not in STATUSES:
        raise HTTPException(status_code=400, detail='Invalid application status')
    return update_tracking(
        payload.source, payload.job_id, payload.saved, payload.status, payload.job
    )


@app.post('/applications/prepare')
def application_preview(payload: ApplicationPrepareRequest):
    return prepare_application(payload.job)
