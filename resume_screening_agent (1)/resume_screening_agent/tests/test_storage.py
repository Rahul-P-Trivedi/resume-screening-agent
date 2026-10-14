"""
Tests for src/storage.py — saving results to JSON and CSV.
"""

import json
import os

import src.storage as storage


def test_save_results_creates_json_and_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "RESULTS_DIR", str(tmp_path))

    fake_results = [
        {
            "file": "a.txt",
            "candidate_name": "A",
            "final_score": 90.0,
            "matched_skills": ["Python", "SQL"],
            "missing_skills": [],
            "strengths": ["Fast learner"],
            "concerns": [],
        }
    ]

    json_path, csv_path = storage.save_results(fake_results, tag="testrun")

    assert os.path.exists(json_path)
    assert os.path.exists(csv_path)

    with open(json_path) as f:
        loaded = json.load(f)
    assert loaded[0]["candidate_name"] == "A"

    with open(csv_path) as f:
        csv_content = f.read()
    assert "Python; SQL" in csv_content  # list fields joined with "; "


def test_save_results_with_empty_list_still_writes_json(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "RESULTS_DIR", str(tmp_path))

    json_path, csv_path = storage.save_results([], tag="empty")

    assert os.path.exists(json_path)
    with open(json_path) as f:
        assert json.load(f) == []
