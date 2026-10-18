
from pathlib import Path

import matplotlib.pyplot as plt


def create_bar_chart(counts, title, x_label, output_path, top_n=10):
    """Create and save a horizontal bar chart."""
    if counts.empty:
        print(f"Skipping chart '{title}': no data available.")
        return

    top_counts = counts.head(top_n)
    top_counts = top_counts.sort_values(ascending=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure_height = max(4, len(top_counts) * 0.5)

    fig, ax = plt.subplots(figsize=(10, figure_height))

    ax.barh(top_counts.index.astype(str), top_counts.values)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")

    print(f"Chart saved to: {output_path}")

    plt.show()
    plt.close(fig)


def create_job_title_chart(job_title_counts, output_dir):
    output_path = Path(output_dir) / "job_title_frequency.png"

    create_bar_chart(
        counts=job_title_counts,
        title="Most Frequent Job Titles",
        x_label="Number of Listings",
        output_path=output_path,
        top_n=10,
    )


def create_skill_chart(skill_counts, output_dir):
    skill_counts = skill_counts[skill_counts > 0]
    skill_counts = skill_counts.head(10)

    output_path = Path(output_dir) / "technical_skill_frequency.png"

    create_bar_chart(
        counts=skill_counts,
        title="Most Frequently Mentioned Technical Skills",
        x_label="Number of Job Listings Mentioning Skill",
        output_path=output_path,
        top_n=10,
    )
