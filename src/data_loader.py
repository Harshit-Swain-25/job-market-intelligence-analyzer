
import json
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"

JOB_COLUMNS = [
    "job_title",
    "company",
    "location",
    "description",
    "job_url",
    "posted_date",
]


def load_sample_jobs(file_path=None):
    """Load fictional job listings from the sample CSV."""
    if file_path is None:
        file_path = PROJECT_ROOT / "data" / "sample_jobs.csv"

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Sample job data was not found: {file_path}"
        )

    try:
        jobs = pd.read_csv(file_path)
    except pd.errors.EmptyDataError as error:
        raise ValueError(
            f"The CSV file is empty: {file_path}"
        ) from error

    if jobs.empty:
        raise ValueError(
            f"The CSV file contains no job listings: {file_path}"
        )

    return jobs


def fetch_remotive_jobs(limit=50):
    """Fetch live remote job listings from the Remotive API."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("The job limit must be an integer.")

    if limit < 1 or limit > 100:
        raise ValueError("The job limit must be between 1 and 100.")

    response = requests.get(
        REMOTIVE_API_URL,
        params={"limit": limit},
        timeout=20,
    )
    response.raise_for_status()

    try:
        payload = response.json()
    except ValueError as error:
        raise ValueError(
            "The Remotive API returned invalid JSON."
        ) from error

    if not isinstance(payload, dict):
        raise TypeError(
            "The Remotive API response must be a JSON object."
        )

    api_jobs = payload.get("jobs")

    if not isinstance(api_jobs, list):
        raise TypeError(
            "The API response must contain a jobs list."
        )

    if not api_jobs:
        raise ValueError(
            "The API returned no job listings for this request."
        )

    normalized_jobs = []

    for job in api_jobs:
        if not isinstance(job, dict):
            continue

        normalized_jobs.append(
            {
                "job_title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location"),
                "description": job.get("description"),
                "job_url": job.get("url"),
                "posted_date": job.get("publication_date"),
            }
        )

    if not normalized_jobs:
        raise ValueError(
            "The API response contains no usable job records."
        )

    return pd.DataFrame(
        normalized_jobs,
        columns=JOB_COLUMNS,
    )


def save_live_jobs(jobs, output_path=None):
    """Save normalized live job listings as a JSON file."""
    if output_path is None:
        output_path = PROJECT_ROOT / "outputs" / "remotive_jobs.json"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = jobs.to_dict(orient="records")

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    return output_path
