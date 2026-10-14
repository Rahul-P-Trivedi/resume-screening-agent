"""
Tests for src/similarity.py — the TF-IDF cosine similarity scorer.
No API key needed: this module is pure local computation.
"""

from src.similarity import compute_similarity_score


def test_identical_text_scores_high():
    text = "Python machine learning scikit-learn pandas numpy Git SQL"
    score = compute_similarity_score(text, text)
    assert score > 90, f"Identical text should score near 100, got {score}"


def test_relevant_resume_scores_higher_than_unrelated():
    jd = "Looking for a Python developer with scikit-learn and pandas experience for machine learning."
    relevant_resume = "I have 2 years experience with Python, scikit-learn, pandas, and building ML models."
    unrelated_resume = "I am a chef specializing in Italian cuisine and restaurant management."

    relevant_score = compute_similarity_score(jd, relevant_resume)
    unrelated_score = compute_similarity_score(jd, unrelated_resume)

    assert relevant_score > unrelated_score


def test_empty_resume_scores_zero():
    jd = "Looking for a Python developer."
    score = compute_similarity_score(jd, "")
    assert score == 0.0


def test_score_is_within_valid_range():
    jd = "Python machine learning engineer with SQL experience."
    resume = "I know some Java and C++ but no Python."
    score = compute_similarity_score(jd, resume)
    assert 0.0 <= score <= 100.0
