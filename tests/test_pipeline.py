
import unittest

import pandas as pd

from src.analyzer import analyze_job_market
from src.data_cleaner import clean_job_data


class TestJobMarketPipeline(unittest.TestCase):
    def setUp(self):
        self.jobs = pd.DataFrame(
            [
                {
                    "job_title": " Python Developer ",
                    "company": "Acme",
                    "location": "Pune",
                    "description": "Python, Git",
                    "job_url": "https://example.com/1",
                },
                {
                    "job_title": "Python Developer",
                    "company": "Acme",
                    "location": "Pune",
                    "description": "Python, Git",
                    "job_url": "https://example.com/1",
                },
                {
                    "job_title": "Backend Developer",
                    "company": "Blue",
                    "location": None,
                    "description": None,
                    "job_url": None,
                },
                {
                    "job_title": None,
                    "company": "Unknown Co",
                    "location": "Delhi",
                    "description": "Python",
                    "job_url": None,
                },
            ]
        )

    def test_cleaning_removes_duplicates_and_invalid_rows(self):
        cleaned_jobs = clean_job_data(self.jobs)

        self.assertEqual(len(cleaned_jobs), 2)
        self.assertEqual(
            cleaned_jobs.iloc[0]["job_title"],
            "Python Developer",
        )

    def test_cleaning_handles_missing_optional_fields(self):
        cleaned_jobs = clean_job_data(self.jobs)

        backend_jobs = cleaned_jobs[
            cleaned_jobs["job_title"] == "Backend Developer"
        ]

        self.assertEqual(len(backend_jobs), 1)
        self.assertEqual(
            backend_jobs.iloc[0]["location"],
            "Unknown",
        )
        self.assertEqual(
            backend_jobs.iloc[0]["description"],
            "",
        )

    def test_analyzer_counts_job_titles(self):
        cleaned_jobs = clean_job_data(self.jobs)
        results = analyze_job_market(cleaned_jobs)

        self.assertEqual(
            results["job_titles"]["Python Developer"],
            1,
        )
        self.assertEqual(
            results["job_titles"]["Backend Developer"],
            1,
        )

    def test_cleaner_rejects_missing_required_columns(self):
        invalid_jobs = pd.DataFrame(
            {"job_title": ["Python Developer"]}
        )

        with self.assertRaises(ValueError):
            clean_job_data(invalid_jobs)


if __name__ == "__main__":
    unittest.main()
