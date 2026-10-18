
import argparse
from pathlib import Path

import requests

from src.analyzer import analyze_job_market
from src.data_cleaner import clean_job_data
from src.data_loader import (
    fetch_remotive_jobs,
    load_sample_jobs,
    save_live_jobs,
)
from src.visualizer import (
    create_job_title_chart,
    create_skill_chart,
)

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"


def save_analysis_results(cleaned_jobs, results):
    """Save the cleaned dataset and analysis summaries."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cleaned_jobs.to_csv(
        OUTPUT_DIR / "cleaned_jobs.csv",
        index=False,
    )

    output_columns = {
        "job_titles": "job_title",
        "companies": "company",
        "locations": "location",
        "skills": "skill",
    }

    for result_name, category_name in output_columns.items():
        summary = results[result_name]

        summary_frame = summary.rename_axis(
            category_name
        ).reset_index(name="listing_count")

        summary_frame.to_csv(
            OUTPUT_DIR / f"{result_name}.csv",
            index=False,
        )


def get_arguments():
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description="Analyze job market listings."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Fetch live listings from the Remotive API.",
    )
    return parser.parse_args()


def main():
    """Run the Job Market Intelligence Analyzer."""
    args = get_arguments()
    data_source = "sample"

    if args.live:
        try:
            jobs = fetch_remotive_jobs(limit=50)
            save_live_jobs(jobs)
            data_source = "Remotive live API"
            print("Successfully retrieved live job listings.")
        except (requests.RequestException, ValueError, OSError) as error:
            print(f"Live data retrieval failed: {error}")
            print("Falling back to the fictional sample dataset.")

            try:
                jobs = load_sample_jobs()
            except (FileNotFoundError, ValueError, OSError) as sample_error:
                print(f"Could not load sample data: {sample_error}")
                return
    else:
        try:
            jobs = load_sample_jobs()
        except (FileNotFoundError, ValueError, OSError) as error:
            print(f"Could not load sample data: {error}")
            return

    try:
        cleaned_jobs = clean_job_data(jobs)
    except ValueError as error:
        print(f"Could not clean job data: {error}")
        return

    print("\nJob Market Intelligence Analyzer")
    print("-" * 35)
    print(f"Data source: {data_source}")
    print(f"Listings loaded: {len(jobs)}")
    print(f"Listings after cleaning: {len(cleaned_jobs)}")
    print(
        "Listings removed during cleaning: "
        f"{len(jobs) - len(cleaned_jobs)}"
    )

    if cleaned_jobs.empty:
        print("\nNo valid job listings are available for analysis.")
        return

    try:
        results = analyze_job_market(cleaned_jobs)
    except ValueError as error:
        print(f"Could not analyze job data: {error}")
        return

    print("\nJob Titles:")
    print(results["job_titles"].to_string())

    print("\nCompanies:")
    print(results["companies"].to_string())

    print("\nLocations:")
    print(results["locations"].to_string())

    print("\nTechnical Skills:")
    skill_counts = results["skills"]
    skill_counts = skill_counts[skill_counts > 0]
    print(skill_counts.to_string())

    try:
        save_analysis_results(cleaned_jobs, results)
        print(f"\nAnalysis results saved to: {OUTPUT_DIR}")
    except (OSError, ValueError) as error:
        print(f"Could not save analysis results: {error}")
        return

    try:
        print("\nGenerating visualizations...")

        create_job_title_chart(results["job_titles"], OUTPUT_DIR)
        create_skill_chart(results["skills"], OUTPUT_DIR)

    except (OSError, ValueError) as error:
        print(f"Could not generate visualizations: {error}")
        return

    print("\nAnalysis and visualization complete.")


if __name__ == "__main__":
    main()
