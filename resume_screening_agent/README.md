# AI Resume Screening Agent

An agent that takes **a job description and a folder of resumes**, and produces
**a ranked shortlist of candidates**, each with a fit score, matched/missing
skills, strengths, concerns, and a short rationale — via a command-line tool.

> **One-sentence spec:** *My agent takes a job description + a folder of resumes
> and produces a ranked, explained shortlist of candidates.*

---

## How it works (Input → Think → Act → Output)

```
User runs `python agent.py`
        │
        ▼
Load job description + all resumes from disk (file_reader.py)
        │
        ▼
For each resume:
  ├─ TF-IDF cosine similarity vs. JD  (similarity.py — fast, deterministic)
  └─ Claude API structured judgement  (llm_screener.py — reasoning-based)
        │
        ▼
Combine into one weighted final_score, sort candidates (scorer.py)
        │
        ▼
Display ranked table in terminal + save full results to JSON & CSV (storage.py)
        │
        ▼
Interactive follow-up loop: type a candidate's name for full detail
```

---

## Project structure

```
resume_screening_agent/
├── agent.py                  # CLI entry point / main loop
├── src/
│   ├── config.py              # env vars, weights, the system prompt
│   ├── file_reader.py         # loads .txt / .pdf resumes & JD
│   ├── similarity.py          # TF-IDF cosine similarity scoring
│   ├── llm_screener.py        # Claude API call + JSON parsing
│   ├── scorer.py               # combines similarity + LLM into final ranking
│   └── storage.py             # saves results to results/*.json and *.csv
├── data/
│   ├── job_description.txt    # sample JD (Junior AI/ML Research Associate)
│   └── resumes/                # 5 sample resumes (varying fit levels)
├── sample_output/              # example run for reviewers who don't run it live
│   ├── example_results.json
│   ├── example_results.csv
│   └── example_terminal_transcript.txt
├── results/                    # your real runs are saved here (gitkeep only, empty in repo)
├── requirements.txt
└── .env.example
```

---

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd resume_screening_agent
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and paste in your Anthropic API key (get one at
https://console.anthropic.com/settings/keys):

```
ANTHROPIC_API_KEY=sk-ant-...
```

`.env` is only read locally by `python-dotenv` — never commit it (already
covered by the `.gitignore` below).

### 3. Run it

```bash
python agent.py
```

This screens the 5 bundled sample resumes against the bundled sample job
description, prints a ranked table, saves full results to `results/`, then
drops you into a small interactive loop where you can type a candidate's name
to see the full breakdown.

### 4. Run it on your own data

```bash
python agent.py --jd path/to/your_job_description.txt --resumes path/to/your_resumes_folder
```

Other flags:
- `--top N` — show only the top N candidates in the summary table (default 5)
- `--no-interactive` — run once, print + save results, then exit (useful for scripting)

Resumes can be `.txt` or `.pdf`. Just drop files into a folder — no naming
convention required.

---

## Sample input & output

- Sample JD: [`data/job_description.txt`](data/job_description.txt)
- Sample resumes: [`data/resumes/`](data/resumes/) (5 candidates: a strong ML
  fit, a partial fit from an adjacent field, a weaker junior candidate, and a
  clearly unrelated frontend developer, to demonstrate score spread)
- Example output: [`sample_output/example_results.json`](sample_output/example_results.json),
  [`sample_output/example_results.csv`](sample_output/example_results.csv),
  and a full terminal transcript at
  [`sample_output/example_terminal_transcript.txt`](sample_output/example_terminal_transcript.txt)

These sample outputs were generated from one real run against the bundled
data and are included so reviewers can see expected behavior without
necessarily needing their own API key first.

---

## Design choices

**Two scoring signals, combined.** The rubric asks specifically for an NLP
similarity method *and* a model choice, so the agent uses both instead of
picking one:
- **TF-IDF + cosine similarity** (`similarity.py`) — fast, deterministic,
  free, and easy to sanity-check. Good at catching keyword/phrase overlap
  (e.g. "machine learning", "scikit-learn").
- **Claude (`claude-sonnet-4-6`) structured judgement** (`llm_screener.py`) —
  understands *context*, e.g. that "built a spam classifier with scikit-learn"
  demonstrates a required skill even if the resume never says the literal
  phrase "machine learning framework." This is where most of the real
  screening intelligence lives.

Final score = `0.4 × similarity + 0.6 × LLM score` (both weights configurable
in `.env`). The LLM is weighted higher because it's the one actually reading
for *meaning*; TF-IDF is there mainly as a cheap, explainable sanity check and
to slightly dampen cases where the LLM might be swayed by confident wording
alone.

**Structured JSON output, not free text.** The system prompt (`config.py`)
forces Claude to return one strict JSON object per resume (score, matched/
missing skills, strengths, concerns, rationale). This makes results
programmatically sortable/exportable rather than something a human has to
re-read and re-interpret every time.

**One resume = one API call.** Simpler and more reliable than batching
multiple resumes into a single prompt, at the cost of more API calls for
large batches (see Tradeoffs).

**CLI over a full web UI.** The brief says a UI is optional and reviewers
score what they can run — a single `python agent.py` command with a clear
README is the most foolproof thing to hand a reviewer with no other context.

---

## Tradeoffs & what I'd improve with more time

- **Cost/latency scales linearly with resume count.** One LLM call per
  resume is simple and reliable, but screening 500 resumes means 500 API
  calls. With more time I'd add batching (e.g. Claude's Message Batches API)
  or a cheap first-pass filter (pure TF-IDF threshold) to cut obviously
  irrelevant resumes before spending LLM calls on them.
- **TF-IDF is shallow.** It doesn't understand synonyms (e.g. "NLP" vs
  "natural language processing") the way embeddings would. A production
  version would likely swap TF-IDF for a proper sentence-embedding model
  (or use a dedicated embeddings API) for the similarity leg, while keeping
  it as a second signal alongside the LLM.
- **No PII redaction.** Real resumes contain personal contact info. A
  production tool should strip or mask this before logging/storing results.
- **No de-duplication or resume-quality checks.** E.g. two resumes for the
  same candidate, or a corrupted/empty PDF, are handled minimally right now
  (a load warning, not a smart merge/skip).
- **Fixed rubric in the prompt.** The scoring bands (80-100 / 50-79 / 0-49)
  are hard-coded in the system prompt. A more flexible version would let the
  hiring manager tune weighting per-requirement (e.g. "must-have" vs
  "nice-to-have" skills affecting the score differently).
- **No persistence/database.** Results are JSON/CSV files per run. For a
  real recruiting pipeline, this would move to SQLite/Postgres so results
  could be queried, compared across job postings, and tracked over time.

---

## Explaining the code

Every module is small and single-purpose on purpose:
- `file_reader.py` — pure I/O, no logic
- `similarity.py` — one pure function, no side effects
- `llm_screener.py` — the only place that talks to the network
- `scorer.py` — orchestrates the above two into one result per candidate
- `storage.py` — the only place that writes to disk
- `agent.py` — CLI glue: argument parsing, the loop, printing

This separation was intentional so each piece can be explained, tested, or
swapped independently (e.g. replacing TF-IDF with embeddings only touches
`similarity.py`).
