import re

import pandas as pd

TECHNICAL_SKILLS = [
    "Python",
    "JavaScript",
    "FastAPI",
    "Django",
    "Flask",
    "pandas",
    "NumPy",
    "Matplotlib",
    "SQL",
    "Git",
    "Docker",
    "REST API",
    "machine learning",
]


def count_job_titles(jobs):
    return jobs["job_title"].value_counts()


def count_companies(jobs):
    return jobs["company"].value_counts()


def count_locations(jobs):
    return jobs["location"].value_counts()


def count_technical_skills(jobs):
    skill_counts = {}

    for skill in TECHNICAL_SKILLS:
        count = 0
        skill_pattern = re.compile(
            rf"\b{re.escape(skill)}\b",
            flags=re.IGNORECASE,
        )

        for description in jobs["description"]:
            if skill_pattern.search(str(description)):
                count += 1

        skill_counts[skill] = count

    sorted_counts = sorted(
        skill_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return pd.Series(
        dict(sorted_counts),
        name="listing_count",
        dtype="int64",
    )


def analyze_job_market(jobs):
    required_columns = [
        "job_title",
        "company",
        "location",
        "description",
    ]

    missing_columns = [
        column for column in required_columns if column not in jobs.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    return {
        "job_titles": count_job_titles(jobs),
        "companies": count_companies(jobs),
        "locations": count_locations(jobs),
        "skills": count_technical_skills(jobs),
    }
