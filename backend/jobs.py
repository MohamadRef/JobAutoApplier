import requests

JOBS_API = "https://remotive.com/api/remote-jobs"

INTERNSHIP_KEYWORDS = [
    "intern",
    "internship",
    "co-op",
    "coop"
]

TECH_KEYWORDS = [
    "software",
    "developer",
    "engineering",
    "backend",
    "frontend",
    "full stack",
    "full-stack",
    "machine learning",
    "artificial intelligence",
    "data science",
    "embedded"
]


def get_jobs():
    response = requests.get(JOBS_API, timeout=15)
    response.raise_for_status()

    data = response.json()
    jobs = []

    for job in data.get("jobs", []):
        title = job.get("title", "").lower()
        location = job.get("candidate_required_location", "").lower()

        is_internship = any(
            keyword in title for keyword in INTERNSHIP_KEYWORDS
        )

        is_tech = any(
            keyword in title for keyword in TECH_KEYWORDS
        )

        is_canada = (
            "canada" in location
            or "worldwide" in location
        )

        if is_internship and is_tech and is_canada:
            jobs.append({
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location"),
                "url": job.get("url")
            })

    return jobs