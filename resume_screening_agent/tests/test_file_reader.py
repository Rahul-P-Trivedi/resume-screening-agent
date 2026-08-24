"""
Tests for src/file_reader.py — reading resumes and job descriptions off disk.
"""

import os
import pytest

from src.file_reader import read_document, load_resumes


def test_read_text_file(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("Hello resume content", encoding="utf-8")
    content = read_document(str(f))
    assert content == "Hello resume content"


def test_load_resumes_from_folder(tmp_path):
    (tmp_path / "resume_a.txt").write_text("Candidate A resume", encoding="utf-8")
    (tmp_path / "resume_b.txt").write_text("Candidate B resume", encoding="utf-8")
    (tmp_path / "notes.md").write_text("should be ignored, wrong extension", encoding="utf-8")

    resumes = load_resumes(str(tmp_path))

    assert len(resumes) == 2
    assert "resume_a.txt" in resumes
    assert "resume_b.txt" in resumes
    assert "notes.md" not in resumes
    assert resumes["resume_a.txt"] == "Candidate A resume"


def test_load_resumes_missing_folder_raises():
    with pytest.raises(FileNotFoundError):
        load_resumes("/path/does/not/exist")


def test_load_resumes_empty_folder_returns_empty_dict(tmp_path):
    resumes = load_resumes(str(tmp_path))
    assert resumes == {}


def test_bundled_sample_data_loads():
    """Sanity check that the shipped sample data in data/ is valid and loadable."""
    jd_path = os.path.join("data", "job_description.txt")
    resumes_dir = os.path.join("data", "resumes")

    jd_text = read_document(jd_path)
    assert len(jd_text) > 50

    resumes = load_resumes(resumes_dir)
    assert len(resumes) == 5
    for name, text in resumes.items():
        assert len(text) > 20, f"{name} looks empty or too short"
