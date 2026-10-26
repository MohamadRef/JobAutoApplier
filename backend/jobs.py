import requests

JOBS_API = "https://remotive.com/api/remote-jobs"
HIMALAYAS_API = "https://himalayas.app/jobs/api/search"

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
        title = (job.get("title") or "").lower()
        location = (job.get("candidate_required_location") or "").lower()

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
                "url": job.get("url"),
                "source": "Remotive"
            })

    return jobs


def get_himalayas_jobs():
    response = requests.get(
        HIMALAYAS_API,
        params={
            "q": "software engineer",
            "country": "CA",
            "employment_type": "Intern"
        },
        timeout=15
    )
    response.raise_for_status()

    data = response.json()
    jobs = []

    for job in data.get("jobs", []):
        title = (job.get("title") or "").lower()

        is_internship = (
            any(keyword in title for keyword in INTERNSHIP_KEYWORDS)
            or job.get("employmentType") == "Intern"
        )

        is_tech = any(
            keyword in title for keyword in TECH_KEYWORDS
        )

        if is_internship and is_tech:
            jobs.append({
                "id": job.get("guid"),
                "title": job.get("title"),
                "company": job.get("companyName"),
                "location": job.get("locationRestrictions") or ["Worldwide"],
                "url": job.get("applicationLink"),
                "source": "Himalayas"
            })

    return jobs