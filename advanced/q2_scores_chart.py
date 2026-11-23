"""
Q2 - Data Processing and Visualization (larger version)

Fetches 100 students' test scores from an API, calculates average, median,
highest, lowest and grade distribution, and saves two charts:
  - scores_bar_chart.png : top 20 students with the class average line
  - grade_distribution.png : how many students got each grade

If the API is not reachable, it falls back to ../data/scores.json.

Usage:
    python q2_scores_chart.py
    python q2_scores_chart.py --api-url https://your-api/scores --show
"""

import argparse
import json
import logging
import statistics
from collections import Counter
from pathlib import Path

import matplotlib
import requests

log = logging.getLogger("scores")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

DEFAULT_API = "https://example.com/api/scores"
FALLBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "scores.json"


def fetch_scores(api_url: str) -> list[dict]:
    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as e:
        log.warning("API not reachable (%s). Using %s", e.__class__.__name__, FALLBACK_FILE.name)
        return json.loads(FALLBACK_FILE.read_text())


def clean(students: list[dict]) -> list[dict]:
    good = []
    for s in students:
        try:
            score = float(s["score"])
        except (KeyError, TypeError, ValueError):
            continue
        if 0 <= score <= 100 and s.get("name"):
            good.append({"name": s["name"], "score": score})
    return good


def grade(score: float) -> str:
    if score >= 90: return "A"
    if score >= 75: return "B"
    if score >= 60: return "C"
    if score >= 40: return "D"
    return "F"


def summarize(students: list[dict]) -> dict:
    scores = [s["score"] for s in students]
    return {
        "count": len(scores),
        "average": round(statistics.mean(scores), 2),
        "median": statistics.median(scores),
        "highest": max(students, key=lambda s: s["score"]),
        "lowest": min(students, key=lambda s: s["score"]),
        "grades": Counter(grade(x) for x in scores),
    }


def plot(students: list[dict], stats: dict, show: bool) -> None:
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    top = sorted(students, key=lambda s: s["score"], reverse=True)[:20]
    plt.figure(figsize=(12, 5))
    plt.bar([s["name"] for s in top], [s["score"] for s in top], color="skyblue")
    plt.axhline(stats["average"], color="red", linestyle="--", label=f"Class average = {stats['average']}")
    plt.title("Top 20 Students - Test Scores")
    plt.ylabel("Score"); plt.ylim(0, 105)
    plt.xticks(rotation=60, ha="right")
    plt.legend(); plt.tight_layout()
    plt.savefig("scores_bar_chart.png", dpi=150)

    plt.figure(figsize=(6, 4))
    order = ["A", "B", "C", "D", "F"]
    plt.bar(order, [stats["grades"].get(g, 0) for g in order], color="lightgreen")
    plt.title("Grade Distribution"); plt.xlabel("Grade"); plt.ylabel("Students")
    plt.tight_layout()
    plt.savefig("grade_distribution.png", dpi=150)

    if show:
        plt.show()
    log.info("Saved scores_bar_chart.png and grade_distribution.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default=DEFAULT_API)
    parser.add_argument("--show", action="store_true", help="open the charts in a window")
    args = parser.parse_args()

    students = clean(fetch_scores(args.api_url))
    stats = summarize(students)

    print(f"\nStudents      : {stats['count']}")
    print(f"Average score : {stats['average']}")
    print(f"Median score  : {stats['median']}")
    print(f"Highest       : {stats['highest']['name']} ({stats['highest']['score']:.0f})")
    print(f"Lowest        : {stats['lowest']['name']} ({stats['lowest']['score']:.0f})")
    print("Grades        : " + ", ".join(f"{g}={stats['grades'].get(g, 0)}" for g in "ABCDF"))

    plot(students, stats, args.show)


if __name__ == "__main__":
    main()
