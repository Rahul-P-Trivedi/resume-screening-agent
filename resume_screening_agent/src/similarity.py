"""
NLP similarity method used alongside the LLM judgement.

This uses TF-IDF (Term Frequency - Inverse Document Frequency) vectorization
plus cosine similarity to give a fast, deterministic, explainable "keyword
and phrase overlap" score between a job description and a resume.

Why TF-IDF and not embeddings?
- No extra API calls / cost / latency (runs fully offline in scikit-learn)
- Deterministic and reproducible — same inputs always give same score
- Easy for a reviewer to understand and sanity-check
- Complements the LLM score, which judges *quality* of fit rather than
  just word overlap. See README "Design Choices" for the trade-off discussion.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity_score(job_description: str, resume_text: str) -> float:
    """
    Returns a 0-100 similarity score between the JD and a single resume,
    based on TF-IDF cosine similarity.
    """
    if not resume_text.strip():
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),  # unigrams + bigrams catch phrases like "machine learning"
    )

    try:
        tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
    except ValueError:
        # Happens if vocabulary is empty after stop-word removal
        return 0.0

    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(sim) * 100, 2)
