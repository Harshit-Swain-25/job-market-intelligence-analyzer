import pandas as pd


def clean_job_data(jobs):
    required_columns = ["job_title", "company", "location", "description", "job_url"]

    missing_columns = [
        column for column in required_columns if column not in jobs.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    cleaned_jobs = jobs.copy()

    text_columns = cleaned_jobs.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        cleaned_jobs[column] = cleaned_jobs[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

        cleaned_jobs[column] = cleaned_jobs[column].replace("", pd.NA)

    cleaned_jobs = cleaned_jobs.dropna(subset=["job_title", "company"])

    cleaned_jobs["location"] = cleaned_jobs["location"].fillna("Unknown")
    cleaned_jobs["description"] = cleaned_jobs["description"].fillna("")

    has_url = cleaned_jobs["job_url"].notna() & cleaned_jobs["job_url"].ne("")

    jobs_with_url = cleaned_jobs[has_url].drop_duplicates(subset=["job_url"])

    jobs_without_url = cleaned_jobs[~has_url].drop_duplicates(
        subset=[
            "job_title",
            "company",
            "location",
            "description",
        ]
    )

    cleaned_jobs = pd.concat([jobs_with_url, jobs_without_url]).sort_index()

    return cleaned_jobs.reset_index(drop=True)
