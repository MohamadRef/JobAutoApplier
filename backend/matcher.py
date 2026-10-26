import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.profile import SKILLS
from backend.resume import get_resume_text

SKILL_ALIASES = {
    "Python": ["python"],
    "JavaScript": ["javascript"],
    "TypeScript": ["typescript"],
    "Java": ["java"],
    "C": ["c"],
    "C++": ["c++"],
    "React": ["react", "react.js"],
    "Node.js": ["node.js", "nodejs"],
    "HTML": ["html"],
    "CSS": ["css"],
    "Tailwind CSS": ["tailwind"],
    "REST APIs": ["rest api", "restful api", "rest apis"],
    "Git": ["git"],
    "GitHub": ["github"],
    "GitLab": ["gitlab"],
    "Linux": ["linux"],
    "Docker": ["docker"],
    "MySQL": ["mysql"],
    "SQL": ["sql"],
    "CI/CD": ["ci/cd", "continuous integration"],
    "Automation": ["automation", "automated testing"],
    "Embedded Systems": ["embedded systems", "embedded software"],
    "Firmware": ["firmware"],
    "Machine Learning": ["machine learning", "ml models"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "Spring Boot": ["spring boot", "springboot"],
    "PostgreSQL": ["postgresql", "postgres"],
    "Kubernetes": ["kubernetes", "k8s"],
    "PyTorch": ["pytorch"],
    "TensorFlow": ["tensorflow"],
    "GraphQL": ["graphql"],
    "Redis": ["redis"],
    "NestJS": ["nestjs"]
}


def contains_skill(text, aliases):
    for alias in aliases:
        pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def extract_skills(text):
    found = []

    for skill, aliases in SKILL_ALIASES.items():
        if contains_skill(text, aliases):
            found.append(skill)

    return found


def calculate_similarity(resume_text, jobs):
    descriptions = [
        (job.get("title") or "") + " " +
        (job.get("description") or "")
        for job in jobs
    ]

    documents = [resume_text] + descriptions

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=10000
    )

    matrix = vectorizer.fit_transform(documents)

    similarities = cosine_similarity(
        matrix[0:1],
        matrix[1:]
    )[0]

    return similarities


def rank_jobs(jobs):
    if not jobs:
        return []

    resume_text = get_resume_text()
    has_resume = bool(resume_text.strip())

    if has_resume:
        user_skills = set(extract_skills(resume_text))
        similarities = calculate_similarity(resume_text, jobs)
    else:
        user_skills = set(SKILLS)
        similarities = [0.0] * len(jobs)

    ranked = []

    for index, job in enumerate(jobs):
        description = job.get("description") or ""

        job_skills = extract_skills(description)

        matched = [
            skill for skill in job_skills
            if skill in user_skills
        ]

        missing = [
            skill for skill in job_skills
            if skill not in user_skills
        ]

        if job_skills:
            skill_score = (
                len(matched) / len(job_skills)
            ) * 100
        else:
            skill_score = None

        if has_resume:
            similarity_score = float(similarities[index]) * 100

            if skill_score is not None:
                final_score = round(
                    0.7 * skill_score +
                    0.3 * similarity_score
                )
            else:
                final_score = round(similarity_score)

            method = "TF-IDF + Skills"

        else:
            similarity_score = None
            final_score = (
                round(skill_score)
                if skill_score is not None
                else None
            )
            method = "Skills Only"

        ranked.append({
            **job,
            "match_score": final_score,
            "skill_score": (
                round(skill_score)
                if skill_score is not None
                else None
            ),
            "similarity_score": (
                round(similarity_score, 1)
                if similarity_score is not None
                else None
            ),
            "match_method": method,
            "matched_skills": matched,
            "missing_skills": missing,
            "detected_job_skills": job_skills
        })

    ranked.sort(
        key=lambda job: (
            job["match_score"] is not None,
            job["match_score"] or 0
        ),
        reverse=True
    )

    return ranked