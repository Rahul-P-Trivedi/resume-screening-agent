"""
Combines the TF-IDF similarity score and the LLM judgement score into one
final ranked list. This is the "Think" step of the Input -> Think -> Act ->
Output loop.
"""

from src.config import SIMILARITY_WEIGHT, LLM_WEIGHT
from src.similarity import compute_similarity_score
from src.llm_screener import screen_resume


def screen_one_candidate(job_description: str, resume_text: str, filename: str) -> dict:
    """
    Runs both scoring methods for a single resume and merges them into
    one result record.
    """
    similarity_score = compute_similarity_score(job_description, resume_text)

    llm_result = screen_resume(job_description, resume_text, filename)
    llm_score = llm_result.get("match_score", 0)

    final_score = round(SIMILARITY_WEIGHT * similarity_score + LLM_WEIGHT * llm_score, 2)

    return {
        "file": filename,
        "candidate_name": llm_result.get("candidate_name", filename),
        "final_score": final_score,
        "similarity_score": similarity_score,
        "llm_score": llm_score,
        "recommendation": llm_result.get("recommendation", "Unknown"),
        "years_experience_estimate": llm_result.get("years_experience_estimate", "not specified"),
        "matched_skills": llm_result.get("matched_skills", []),
        "missing_skills": llm_result.get("missing_skills", []),
        "strengths": llm_result.get("strengths", []),
        "concerns": llm_result.get("concerns", []),
        "rationale": llm_result.get("rationale", ""),
    }


def screen_all_candidates(job_description: str, resumes: dict) -> list:
    """
    resumes: {filename: resume_text}
    Returns a list of result dicts, sorted by final_score descending.
    """
    results = []
    for filename, resume_text in resumes.items():
        print(f"  Screening {filename} ...")
        try:
            result = screen_one_candidate(job_description, resume_text, filename)
            results.append(result)
        except Exception as e:
            print(f"  [error] Failed to screen {filename}: {e}")

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results
