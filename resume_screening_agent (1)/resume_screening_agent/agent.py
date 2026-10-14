#!/usr/bin/env python3
"""
AI Resume Screening Agent — CLI entry point.

STEP 5: this file wires everything together into the
Input -> Fetch data -> Send to LLM -> Receive answer -> Display -> Save loop.

Usage:
    python agent.py                                  # uses default sample data
    python agent.py --jd path/to/jd.txt --resumes path/to/folder
    python agent.py --top 3                          # show only top 3 in table
"""

import argparse
import os
import sys

from tabulate import tabulate

from src.file_reader import read_document, load_resumes
from src.scorer import screen_all_candidates
from src.storage import save_results

DEFAULT_JD = os.path.join("data", "job_description.txt")
DEFAULT_RESUME_DIR = os.path.join("data", "resumes")


def print_summary_table(results: list, top_n: int):
    table_rows = []
    for r in results[:top_n]:
        table_rows.append([
            r["candidate_name"],
            r["final_score"],
            r["similarity_score"],
            r["llm_score"],
            r["recommendation"],
        ])
    headers = ["Candidate", "Final Score", "Similarity", "LLM Score", "Recommendation"]
    print("\n" + tabulate(table_rows, headers=headers, tablefmt="grid"))


def print_candidate_detail(result: dict):
    print(f"\n--- {result['candidate_name']} ({result['file']}) ---")
    print(f"Final Score: {result['final_score']}  |  Recommendation: {result['recommendation']}")
    print(f"Similarity (TF-IDF): {result['similarity_score']}  |  LLM Judgement: {result['llm_score']}")
    print(f"Estimated Experience: {result['years_experience_estimate']}")
    print(f"Matched Skills: {', '.join(result['matched_skills']) or 'none'}")
    print(f"Missing Skills: {', '.join(result['missing_skills']) or 'none'}")
    print(f"Strengths: {', '.join(result['strengths']) or 'none'}")
    print(f"Concerns: {', '.join(result['concerns']) or 'none'}")
    print(f"Rationale: {result['rationale']}")


def run_screening(jd_path: str, resume_dir: str, top_n: int):
    print(f"\nLoading job description from: {jd_path}")
    job_description = read_document(jd_path)

    print(f"Loading resumes from: {resume_dir}")
    resumes = load_resumes(resume_dir)
    if not resumes:
        print("No .txt or .pdf resumes found in that folder. Nothing to screen.")
        return []

    print(f"Found {len(resumes)} resume(s). Screening now (this calls the Claude API)...\n")
    results = screen_all_candidates(job_description, resumes)

    if not results:
        print("No results produced (all candidates failed to screen — check errors above).")
        return []

    print_summary_table(results, top_n)

    json_path, csv_path = save_results(results)
    print(f"\nSaved full results to:\n  {json_path}\n  {csv_path}")

    return results


def interactive_loop(results: list):
    """Simple follow-up loop so a reviewer can inspect specific candidates
    after the initial screening run, without re-calling the API."""
    if not results:
        return

    print("\nType a candidate's name (or part of it) to see full details, "
          "'list' to see the ranking again, or 'exit' to quit.")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye.")
            break
        if user_input.lower() == "list":
            print_summary_table(results, len(results))
            continue

        matches = [r for r in results if user_input.lower() in r["candidate_name"].lower()]
        if not matches:
            print(f"No candidate matching '{user_input}'. Try 'list' to see all names.")
            continue
        for m in matches:
            print_candidate_detail(m)


def main():
    parser = argparse.ArgumentParser(description="AI Resume Screening Agent")
    parser.add_argument("--jd", default=DEFAULT_JD, help="Path to job description (.txt or .pdf)")
    parser.add_argument("--resumes", default=DEFAULT_RESUME_DIR, help="Folder containing resumes (.txt/.pdf)")
    parser.add_argument("--top", type=int, default=5, help="Number of top candidates to show in the summary table")
    parser.add_argument("--no-interactive", action="store_true", help="Run once and exit, skip the Q&A loop")
    args = parser.parse_args()

    print("=" * 60)
    print("AI RESUME SCREENING AGENT")
    print("=" * 60)

    try:
        results = run_screening(args.jd, args.resumes, args.top)
    except FileNotFoundError as e:
        print(f"\n[error] {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n[error] {e}")
        print("Tip: copy .env.example to .env and add your ANTHROPIC_API_KEY.")
        sys.exit(1)

    if not args.no_interactive:
        interactive_loop(results)


if __name__ == "__main__":
    main()
