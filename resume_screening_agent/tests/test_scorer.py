"""
Tests for src/scorer.py — combining similarity + LLM scores into a ranked
list. The Claude API call is mocked so these tests run offline, free, and
fast (no API key required in CI).
"""

from unittest.mock import patch

from src.scorer import screen_one_candidate, screen_all_candidates


FAKE_LLM_RESPONSE = {
    "candidate_name": "Test Candidate",
    "match_score": 80,
    "recommendation": "Strong Fit",
    "years_experience_estimate": "2 years",
    "matched_skills": ["Python", "SQL"],
    "missing_skills": ["AWS"],
    "strengths": ["Solid Python fundamentals"],
    "concerns": ["No cloud experience"],
    "rationale": "Good overall match with one gap.",
}


@patch("src.scorer.screen_resume", return_value=FAKE_LLM_RESPONSE)
def test_screen_one_candidate_combines_scores(mock_llm):
    jd = "Python developer with SQL and AWS experience."
    resume_text = "I have 2 years of Python and SQL experience."

    result = screen_one_candidate(jd, resume_text, "candidate.txt")

    assert result["candidate_name"] == "Test Candidate"
    assert result["llm_score"] == 80
    assert result["final_score"] > 0
    assert "similarity_score" in result
    assert result["recommendation"] == "Strong Fit"
    mock_llm.assert_called_once()


@patch("src.scorer.screen_resume", return_value=FAKE_LLM_RESPONSE)
def test_screen_all_candidates_returns_sorted_results(mock_llm):
    jd = "Python developer with SQL and AWS experience."
    resumes = {
        "a.txt": "Python and SQL experience.",
        "b.txt": "Python, SQL, and AWS experience.",
    }

    results = screen_all_candidates(jd, resumes)

    assert len(results) == 2
    # results must be sorted descending by final_score
    assert results[0]["final_score"] >= results[1]["final_score"]


@patch("src.scorer.screen_resume", side_effect=RuntimeError("API failure"))
def test_screen_all_candidates_skips_failed_resume_gracefully(mock_llm):
    jd = "Python developer."
    resumes = {"broken.txt": "some resume text"}

    results = screen_all_candidates(jd, resumes)

    # A failed API call should not crash the whole batch — it's just skipped
    assert results == []
