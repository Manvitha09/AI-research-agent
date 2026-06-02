import os
from datetime import datetime


def save_report(topic: str, report: str) -> str:
    """Save the report to a markdown file and return the filename."""
    os.makedirs("reports", exist_ok=True)

    # Clean topic for filename
    safe_topic = "".join(c if c.isalnum() or c in " _-" else "" for c in topic)
    safe_topic = safe_topic.strip().replace(" ", "_")[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/{safe_topic}_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Research Report: {topic}\n")
        f.write(f"*Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}*\n\n")
        f.write(report)

    return filename