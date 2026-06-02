import json
import time
from datetime import datetime
from agent import run_agent
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# -------------------------------------------------------
# TEST CASES
# Each test case has:
#   topic        - what to research
#   must_contain - keywords the report MUST mention
#   must_not     - things the report should NOT say
#   min_words    - minimum report length
# -------------------------------------------------------
TEST_CASES = [
    {
        "id": "TC01",
        "topic": "Kafka vs RabbitMQ",
        "must_contain": ["latency", "throughput", "use case", "queue"],
        "must_not": ["I cannot", "I don't know"],
        "min_words": 200,
    },
    {
        "id": "TC02",
        "topic": "REST vs GraphQL",
        "must_contain": ["overfetching", "schema", "endpoint", "query"],
        "must_not": ["I cannot", "I don't know"],
        "min_words": 200,
    },
    {
        "id": "TC03",
        "topic": "what is docker",
        "must_contain": ["container", "image", "virtual"],
        "must_not": ["I cannot", "I don't know"],
        "min_words": 150,
    },
    {
        "id": "TC04",
        "topic": "best practices for REST APIs",
        "must_contain": ["authentication", "versioning", "status code"],
        "must_not": ["I cannot", "I don't know"],
        "min_words": 150,
    },
]


def score_report(report: str, test_case: dict) -> dict:
    """Score a report against a test case. Returns scores and details."""
    report_lower = report.lower()
    results = {}

    # Check 1: Must-contain keywords
    found_keywords = []
    missing_keywords = []
    for keyword in test_case["must_contain"]:
        if keyword.lower() in report_lower:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    keyword_score = len(found_keywords) / len(test_case["must_contain"]) * 100
    results["keyword_score"] = round(keyword_score)
    results["found_keywords"] = found_keywords
    results["missing_keywords"] = missing_keywords

    # Check 2: Must-not contain
    violations = [w for w in test_case["must_not"] if w.lower() in report_lower]
    results["violations"] = violations
    results["violation_score"] = 0 if violations else 100

    # Check 3: Minimum word count
    word_count = len(report.split())
    results["word_count"] = word_count
    results["length_score"] = 100 if word_count >= test_case["min_words"] else round(
        word_count / test_case["min_words"] * 100
    )

    # Check 4: Has structure (markdown headings)
    heading_count = report.count("##")
    results["has_structure"] = heading_count >= 2
    results["structure_score"] = 100 if heading_count >= 2 else 0

    # Overall score (weighted average)
    results["overall_score"] = round(
        keyword_score * 0.4 +
        results["violation_score"] * 0.2 +
        results["length_score"] * 0.2 +
        results["structure_score"] * 0.2
    )

    return results


def run_evals(test_ids: list = None):
    """Run all (or selected) test cases and print a summary."""
    cases = TEST_CASES
    if test_ids:
        cases = [tc for tc in TEST_CASES if tc["id"] in test_ids]

    console.print(Panel.fit(
        f"[bold blue]🧪 Running Eval Suite[/bold blue]\n[dim]{len(cases)} test cases[/dim]",
        border_style="blue"
    ))

    all_results = []

    for i, tc in enumerate(cases, 1):
        console.print(f"\n[bold]Test {i}/{len(cases)}: {tc['id']} — {tc['topic']}[/bold]")

        start = time.time()
        try:
            report = run_agent(tc["topic"])
            duration = round(time.time() - start, 1)
            scores = score_report(report, tc)
            scores["status"] = "passed" if scores["overall_score"] >= 70 else "failed"
            scores["duration"] = duration
            scores["topic"] = tc["topic"]
            scores["id"] = tc["id"]
            scores["report_preview"] = report[:200] + "..."

        except Exception as e:
            scores = {
                "id": tc["id"],
                "topic": tc["topic"],
                "status": "error",
                "overall_score": 0,
                "error": str(e),
                "duration": round(time.time() - start, 1),
            }
            console.print(f"[red]  ✗ Error: {e}[/red]")

        all_results.append(scores)

        # Print per-test result
        status_color = "green" if scores["status"] == "passed" else "red"
        console.print(f"  [{status_color}]{'✓' if scores['status'] == 'passed' else '✗'} Score: {scores.get('overall_score', 0)}/100 ({scores['status']}) in {scores['duration']}s[/{status_color}]")
        if scores.get("missing_keywords"):
            console.print(f"  [yellow]  Missing keywords: {scores['missing_keywords']}[/yellow]")

        # Wait between tests to avoid rate limits
        if i < len(cases):
            console.print("[dim]  Waiting 5s before next test...[/dim]")
            time.sleep(5)

    # Summary table
    print_summary(all_results)
    save_eval_results(all_results)


def print_summary(results: list):
    """Print a rich summary table."""
    console.print("\n")
    table = Table(title="📊 Eval Results Summary", border_style="blue")
    table.add_column("ID", style="dim")
    table.add_column("Topic")
    table.add_column("Score", justify="center")
    table.add_column("Keywords", justify="center")
    table.add_column("Length", justify="center")
    table.add_column("Structure", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Time", justify="right")

    passed = 0
    for r in results:
        status = r.get("status", "error")
        score = r.get("overall_score", 0)
        color = "green" if status == "passed" else "red"
        if status == "passed":
            passed += 1

        table.add_row(
            r["id"],
            r["topic"][:35] + ("..." if len(r["topic"]) > 35 else ""),
            f"[{color}]{score}/100[/{color}]",
            f"{r.get('keyword_score', 0)}%",
            f"{r.get('length_score', 0)}%",
            "✓" if r.get("has_structure") else "✗",
            f"[{color}]{status}[/{color}]",
            f"{r.get('duration', 0)}s",
        )

    console.print(table)

    avg_score = round(sum(r.get("overall_score", 0) for r in results) / len(results))
    console.print(f"\n[bold]Overall: {passed}/{len(results)} passed | Avg score: {avg_score}/100[/bold]")


def save_eval_results(results: list):
    """Save eval results to a JSON file for tracking over time."""
    import os
    os.makedirs("evals", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"evals/eval_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "total": len(results),
            "passed": sum(1 for r in results if r.get("status") == "passed"),
            "avg_score": round(sum(r.get("overall_score", 0) for r in results) / len(results)),
            "results": results,
        }, f, indent=2)
    console.print(f"\n[dim]Eval results saved to {filename}[/dim]")


if __name__ == "__main__":
    import sys
    # Optionally pass specific test IDs: python eval.py TC01 TC02
    test_ids = sys.argv[1:] if len(sys.argv) > 1 else None
    run_evals(test_ids)