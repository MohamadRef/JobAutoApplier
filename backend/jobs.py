import requests

REMOTIVE_API = "https://remotive.com/api/remote-jobs"
HIMALAYAS_API = "https://himalayas.app/jobs/api/search"

INTERNSHIP_KEYWORDS = ["intern", "internship", "co-op", "coop"]

TECH_KEYWORDS = [
    "software", "developer", "engineer", "backend",
    "frontend", "full stack", "full-stack", "machine learning",
    "artificial intelligence", "data science", "embedded"
]


def valid_job(job, keyword="", location="Canada"):
    title = (job.get("title") or "").lower()
    company = (job.get("company") or "").lower()
    locations = job.get("location") or []

    if isinstance(locations, list):
        location_text = " ".join(str(x) for x in locations).lower()
    else:
        location_text = str(locations).lower()

    if not any(word in title for word in INTERNSHIP_KEYWORDS):
        return False

    if not any(word in title for word in TECH_KEYWORDS):
        return False

    if "unpaid" in title or "volunteer" in title:
        return False

    if keyword and keyword.lower() not in title:
        return False

    if location:
        requested = location.lower()

        if requested == "canada":
            if not any(x in location_text for x in ["canada", "worldwide"]):
                return False
        elif requested not in location_text:
            return False

    if not company or not job.get("url"):
        return False

    return True


def get_jobs():
    response = requests.get(REMOTIVE_API, timeout=15)
    response.raise_for_status()

    jobs = []

    for item in response.json().get("jobs", []):
        jobs.append({
            "id": str(item.get("id")),
            "title": item.get("title"),
            "company": item.get("company_name"),
            "location": item.get("candidate_required_location"),
            "url": item.get("url"),
            "source": "Remotive"
        })

    return jobs


def get_himalayas_jobs():
    response = requests.get(
        HIMALAYAS_API,
        params={
            "q": "software engineer",
            "country": "CA",
            "employment_type": "Intern",
            "sort": "recent"
        },
        timeout=15
    )
    response.raise_for_status()

    jobs = []

    for item in response.json().get("jobs", []):
        jobs.append({
            "id": str(item.get("guid")),
            "title": item.get("title"),
            "company": item.get("companyName"),
            "location": item.get("locationRestrictions") or ["Worldwide"],
            "url": item.get("applicationLink"),
            "source": "Himalayas"
        })

    return jobs


def search_jobs(keyword="", location="Canada"):
    all_jobs = []
    errors = []

    sources = [get_jobs, get_himalayas_jobs]

    for source in sources:
        try:
            all_jobs.extend(source())
        except (requests.RequestException, ValueError) as error:
            errors.append(f"{source.__name__}: {error}")

    filtered_jobs = []
    seen = set()

    for job in all_jobs:
        if not valid_job(job, keyword, location):
            continue

        key = (
            (job["company"] or "").lower().strip(),
            (job["title"] or "").lower().strip()
        )

        if key in seen:
            continue

        seen.add(key)
        filtered_jobs.append(job)

    return filtered_jobs, errors