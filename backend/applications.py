"""Prepare factual, review-first application materials. Does not submit applications."""
from backend.resume import get_resume_text
from backend.matcher import extract_skills


def prepare_application(job):
    title = str(job.get("title") or "Untitled position")
    company = str(job.get("company") or "Unknown company")
    description = str(job.get("description") or "")
    resume = get_resume_text()
    if not resume.strip():
        return {"ready": False, "message": "Upload a PDF resume first.", "company": company, "title": title}

    resume_skills = set(extract_skills(resume))
    job_skills = extract_skills(description)
    matched = [skill for skill in job_skills if skill in resume_skills]
    missing = [skill for skill in job_skills if skill not in resume_skills]

    evidence = (
        "My resume mentions " + ", ".join(matched[:6]) + "."
        if matched else
        "Review the job requirements against my resume before drafting an answer."
    )
    return {
        "ready": True,
        "company": company,
        "title": title,
        "matched_skills": matched,
        "unverified_skills": missing,
        "evidence_summary": evidence,
        "checklist": [
            "Verify role is still open and applications from your location are accepted",
            "Confirm internship dates, pay, and university/co-op restrictions",
            "Review your resume and tailor it without adding unsupported claims",
            "Answer screening questions truthfully",
            "Inspect the complete application before submitting yourself",
        ],
        "application_url": job.get("url"),
        "note": "This prepares a factual checklist; it does not apply or submit anything."
    }
