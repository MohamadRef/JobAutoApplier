import requests

JOBS_API = "https://remotive.com/api/remote-jobs"


def get_jobs():
    response = requests.get(JOBS_API, timeout=15)
    response.raise_for_status()

    data = response.json()
    jobs = []

    for job in data.get("jobs", []):
        title = job.get("title", "")

        if "intern" in title.lower():
            jobs.append({
                "id": job.get("id"),
                "title": title,
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location"),
                "url": job.get("url")
            })

    return jobs