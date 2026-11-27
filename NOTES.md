
# Engineering Notes — DjangoDesk

## D03 — PostgreSQL

### 1. Migration verification

Commands used:

```powershell
uv run alembic downgrade -1
uv run alembic current
uv run alembic upgrade head
uv run alembic history
```

Paste the actual terminal output here.

Current migration head: `22cdb59bd522`

### 2. Loader idempotency

First run:

```text
records=5 inserted=5 updated=0 unchanged=0
```

Second run:

```text
records=5 inserted=0 updated=0 unchanged=5
```

The second run did not insert duplicate records. This confirms idempotency.

**Data note:** The available `data/sample_records.json` contains 5 records. The task mentions 20 records, but the other 15 were not available in the provided project data.

### 3. PostgreSQL GIN index — EXPLAIN ANALYZE

Query:

```sql
EXPLAIN ANALYZE
SELECT id, title
FROM documents
WHERE metadata @> CAST(:f AS jsonb);
```

Filter:

```json
{"page": "ref/models/querysets"}
```

Normal query plan:

```text
Seq Scan on documents  (cost=0.00..11.00 rows=1 width=36) (actual time=0.012..0.014 rows=3.00 loops=1)
  Filter: (metadata @> '{"page": "ref/models/querysets"}'::jsonb)
  Rows Removed by Filter: 2
  Buffers: shared hit=1
Planning:
  Buffers: shared hit=148 read=1
Planning Time: 1.255 ms
Execution Time: 0.036 ms
```

With sequential scans disabled:

```text
Bitmap Heap Scan on documents  (cost=12.81..16.82 rows=1 width=36) (actual time=0.851..0.853 rows=3.00 loops=1)
  Recheck Cond: (metadata @> '{"page": "ref/models/querysets"}'::jsonb)
  Heap Blocks: exact=1
  Buffers: shared hit=3 read=1
  ->  Bitmap Index Scan on ix_documents_metadata_gin  (cost=0.00..12.81 rows=1 width=0) (actual time=0.819..0.819 rows=4.00 loops=1)
        Index Cond: (metadata @> '{"page": "ref/models/querysets"}'::jsonb)
        Index Searches: 1
        Buffers: shared hit=2 read=1
Planning:
  Buffers: shared hit=1
Planning Time: 0.092 ms
Execution Time: 0.898 ms
```

### 4. Why did PostgreSQL choose a Seq Scan?

The table contains only 5 documents. Scanning a small table is cheaper than accessing an index.

### 5. When would PostgreSQL use the GIN index?

When the table becomes larger and the query planner estimates that using the GIN index is cheaper than scanning the entire table.


## D05 — CI/CD, deployment and rollback

### Deployment
- Application deployed to Render: https://djangodesk-iagt.onrender.com
- Health endpoint: `/health`
- Health check returned HTTP 200.
- GitHub Actions CI/CD workflows configured.

### Rollback procedure
If a deployment fails:
1. Identify the last working deployment on Render.
2. Open Render Dashboard → Service → Deploys.
3. Select the previous successful deployment.
4. Roll back to that deployment.
5. Verify `/health` returns HTTP 200.

### Rollback drill — completed

Performed a rollback and roll-forward drill on Render on November 25, 2026.

| Action | Commit SHA | Time (IST) | Result |
|---|---|---|---|
| Original live deployment (Day 7) | `5136cba` | Before 12:17 PM | Live |
| Rollback to Day 6 | `292a9c4` | 12:17:14 PM | Deploy succeeded |
| Roll-forward to Day 7 | `5136cba` | 12:19:13 PM | Deploy succeeded |

#### Rollback verification

- Rollback triggered manually through the Render Dashboard.
- Previous Day 6 deployment became Live.
- `/health` endpoint was checked after rollback.
- Health response returned `status: ok`.
- Application: `djangodesk`
- Environment: `production`

#### Roll-forward verification

- Latest deployment triggered manually through Render Dashboard.
- Restored commit: `5136cba`.
- Deployment status: Deploy succeeded — Live.
- Deployment duration: 50.3 seconds.
- Day 7 version was restored successfully.

#### Result

Rollback to the previous deployment and roll-forward to the latest deployment were both completed successfully.

### Lead time
Lead time was not formally measured during Week 1.

### Smoke test
The deployed application was tested successfully:
- Endpoint: `/health`
- HTTP status: 200
- Application: djangodesk
- Version: dev


## D06 · Collecting the corpus

- Start target: Docs for the current LTS (about 800 pages)
- Collected today: ___ files, ___ pages, ___ MB (from DATASET.md)
- Doors used: URL list / Git repository / sitemap / by hand (keep the ones I used)

### Licence check

| Source | Licence or terms, in my words | May I show full text in answers? |
|---|---|---|
| | | |

### robots.txt

- Site: ________ . Its robots.txt says (2 lines): ________
- Was anything blocked for my bot? What did I do about it?

### Kill and resume

- Run 1: I pressed Ctrl+C after ___ files
- Run 2: downloaded=___ skipped=___
- Run 3: downloaded=0 skipped=___

### Capacity (from docs/CAPACITY.md)

- Tokens per page, measured: ___
- Full corpus: ___ M tokens, ___ chunks, embedding about Rs ___, vectors ___ MB
- The number that surprised me most, and why (2 lines):

### One thing that went wrong today, and how I fixed it

## D07 - Parsing and storing the corpus

### Parsing results

- Files processed: 20
- Successfully parsed: 20
- Failed: 0
- Skipped: 0
- Pages/chunks stored: 3305
- Parser unit tests: 16 passed, 0 failed

### Parser implementation

- PDF: PyMuPDF text extraction, source page numbers, font-based heading detection.
- HTML: Trafilatura extraction with table support.
- Text, Markdown, RST and code files: text cleanup, heading detection and chunking.
- Chunk size: approximately 3000 characters.
- Heading hierarchy: headings are stored with parsed pages.

### Parser comparison: ten complex Django HTML pages

I compared the current Trafilatura extraction (`include_tables=True`) with lxml text extraction scoped to each page's `<main id="main-content">`. These are all ten official-docs HTML pages in the local corpus, including its longest and most code-heavy pages. The figures below are extracted characters / chunks. Code coverage is the percentage of distinct tokens found in the page's `<pre>` and `<code>` blocks that also occur in the extracted text.

| Django docs page | Trafilatura chars / chunks | lxml chars / chunks | Code token types retained (Trafilatura / lxml) |
|---|---:|---:|---:|
| cache | 50,899 / 19 | 50,430 / 17 | 100% / 100% |
| default | 43,810 / 24 | 54,719 / 19 | 83% / 100% |
| deployment | 1,351 / 1 | 2,327 / 1 | 43% / 100% |
| forms | 27,268 / 17 | 28,741 / 10 | 97% / 100% |
| http | 740 / 1 | 449 / 1 | 100% / 100% |
| models | 49,390 / 29 | 51,004 / 18 | 96% / 100% |
| queries | 50,509 / 22 | 62,637 / 21 | 93% / 100% |
| settings | 88,469 / 31 | 103,349 / 35 | 94% / 100% |
| testing | 1,467 / 1 | 1,777 / 1 | 100% / 100% |
| tutorial01 | 9,519 / 4 | 9,709 / 4 | 100% / 100% |

**Result:** lxml retained every measured code-token type in these pages; Trafilatura retained 91% on average, with the largest loss on the short deployment page. Trafilatura generally returned less text than lxml, which can reduce navigation or layout noise. This is a text/code comparison, not a full accuracy score. None of the ten pages has a literal HTML `<table>`, so this sample does not establish table preservation; `include_tables=True` remains enabled in the production HTML parser.

### Bug found and fixed

The HTML parser was receiving HTML content instead of the file path. This caused a FileNotFoundError because the HTML content was interpreted as a filename.

Fixed the HTML parsing call to pass the file path to parse_html().

### Database verification

- Documents: 20
- Pages: 3305
- Parse failures: 0
- Duplicate page records: 0

### Idempotency test

Ran the corpus parser again on the same 20 files. Existing documents and pages were updated instead of duplicated. Verified zero duplicate page records.

### Issue during verification

One run encountered a temporary PostgreSQL connection interruption while processing the PDF. The database connection was checked, and the parser was retried successfully. The final run processed all 20 files with zero failures.

### What I learned

- Parsing is different for PDFs, HTML and plain-text documents.
- HTML content must be passed correctly to the parser.
- Heading paths help preserve document structure.
- Idempotent database storage prevents duplicate records when ingestion is rerun.
- Parse failures should be recorded so failed files can be retried.

### D08 · LLM gateway

#### Models and first-question latency

- Primary model observed in the successful streamed `ask.py` response: Gemini `gemini-3.6-flash` (the local `.env` sets `LLM_PRIMARY_MODEL=gemini-3.6-flash`; the code default is `gemini-3.8-flash`. Render may differ.
- Fallback configured in this checkout: Groq `openai/gpt-oss-20b`.
- Laptop, first question: ___ s; input/output tokens ___ / ___; estimated cost Rs ___; cold start included: ___
- Awake live URL (`https://djangodesk.onrender.com`), first question: ___ s; input/output tokens ___ / ___; estimated cost Rs ___; checked at ___ IST

#### English and Tamil token comparison

Use the same question and prompt on both runs; fill in values from `/v1/chat` or its `done` SSE event.

| Language | Question | Input tokens | Output tokens | Cost (INR) | Latency (ms) |
|---|---|---:|---:|---:|---:|
| English | ___ | ___ | ___ | ___ | ___ |
| Tamil | ___ | ___ | ___ | ___ | ___ |

#### Answers without documents

- Question 6: ___
- Invented or incorrect detail observed: ___
- Off-topic question: declined / answered; observed response: ___

#### Fallback and circuit breaker

- Fallback observed: ___ (configured fallback: Groq `openai/gpt-oss-20b`; usage currently reports 4 fallback calls).
- Circuit breaker: ___ (threshold is 3 consecutive provider failures; cooldown is 30 seconds; after cooldown one probe is allowed).

#### Usage bill

Verified directly against `public.llm_calls` for 2026-11-25: 15 model-call rows, 5 errors, 4 fallback rows, 2,033 input tokens, 1,693 output tokens, and 10 distinct request IDs with an `ok` row. The stored total is Rs 0.0325 (Rs 0.00325 per answered request), but this undercounts the bill: all six successful `gemini-3.6-flash` rows have zero cost because the model was missing from the price map. They used 1,073 input and 793 output tokens. At Google standard paid-tier rates through 2026-12-31 ($0.75/$3.75 per million tokens), the missing estimate is about Rs 0.358957; corrected total is about Rs 0.391448, or Rs 0.03914 per answered request. The gateway price map now includes `gemini-3.6-flash`; this code change affects new calls only. Existing rows remain underpriced until deliberately recalculated. This is a list-price estimate, not a provider invoice.

#### One thing that went wrong today, and how I fixed it

The Neon SQL Editor initially reported that `llm_calls` did not exist. I manually created the table and set `alembic_version` to `d60bed8b2c83`; `uv run alembic current` now reports `d60bed8b2c83 (head)` for the local configured `DATABASE_URL`. Still verify the SQL Editor is on the same Neon project, branch, database, and schema as the application: the local Alembic result alone does not prove the Render process uses that same target. Compare the table definition and indexes with the migration before relying on manually created schema.

## D09 · Prompt versions compared

<!-- prompts:start -->

| Prompt version | Correct | Accuracy | Invalid replies | Avg tokens in |
|---|---|---|---|---|
| classify_v1 | 16/20 | 80% | 0 | 61 |
| classify_v2 | 18/20 | 90% | 0 | 268 |
| classify_v3 | 19/20 | 95% | 0 | 395 |
| classify_v4 | 20/20 | 100% | 0 | 282 |

<!-- prompts:end -->
Version 4 copies version 2 and clarifies that personal questions include the current status of a user's DjangoDesk account, order, or deployment. It scored 20/20 on this test set (version 2 scored 18/20). Version 3's TODO examples were replaced with real examples; it scored 19/20, missing the password-reset email question (line 11, expected personal, got docs). The comparison made 20 new model calls for v3; v1, v2, and v4 results came from cache.


### D09 · Prompts and structured output

- My best router prompt: classify_v4 with 20 / 20
- What I changed in v4, and what happened to the score: Copied v2 and clarified that personal questions include the current status of a user's DjangoDesk account, order, or deployment. Score increased from 18/20 (v2) to 20/20 (v4) on this test set.
- The question my best version still gets wrong (line, wanted, got), and why I think so: None on this 20-question run; v4 had no misses. This small test set does not guarantee perfect results on new questions.
- A label in my test set that I changed after seeing the results (or "none"): none.
- Input tokens per question: v1 61, best version 282. Is the extra accuracy worth it? On this test set, yes: accuracy rose from 80% to 100% for 221 more input tokens per question. I should check more questions before assuming the gain will generalize.

### My contract (DocMeta)

- Fields I kept from my project card: The project card is not present in this repo, so I cannot verify its exact field list. The current contract includes doc_kind, year, language, summary, topics, page, topic, django_version, api_name, and orm_method.
- Fields I deleted, and why they make no sense per document: No deleted fields are recorded in the repo, so I have no evidence to name any.
- The field I tightened, and how: topics must contain 1–6 short values; values are lowercased and duplicates removed. Short string values are trimmed and limited to 80 characters.

### Extraction run

- Prompt version: extract_v1 ? **20 ok, 0 repaired, 0 failed of 20 parsed Django documents** (10 HTML, 1 PDF, 9 text documents in Neon).
- Not finished? Why, and how many are left: Finished; 20 of 20 parsed documents have extraction metadata, with 0 remaining.
- Most common failure reason, and what I did about it: No document extraction failures. Provider quota/rate-limit errors interrupted early attempts; extraction resumed at 3 documents/minute with a 2,500-character input limit and completed.
- A record that was valid but wrong (document, field, what it said, what is true): Not manually audited yet.
- Cost recorded for successful extraction calls: Rs 0.842907 total (about Rs 0.0421 per parsed document); 41,459 input and 19,211 output tokens. The provider also logged 22 failed call attempts with no recorded cost.

### One thing that went wrong today, and how I fixed it

Neon initially contained 20 sample records and no parsed Django documents, so extraction correctly found nothing to process. I parsed the first 20 corpus manifest entries (20 documents) into Neon, then ran extraction. Provider quotas interrupted the first attempts; lowering the rate and input size let the resumable run finish all 20 documents. I also replaced the TODO examples in classify_v3 and reran the prompt comparison.


### D10 · Queue and worker

- First run: ___ documents queued, finished in ___ s. Done ___ , skipped ___ , failed ___
- Pace: ___ s per document (INGEST_RPM = ___ , INGEST_CONCURRENCY = ___ )

### Kill test

- Queued: 20. At the kill: queued ___ , running ___ , done ___ , failed ___
- After the new worker: done ___ + skipped ___ + failed ___ = ___ (must be 20)
- Documents in the database: ___ , different ids: ___ (must be equal)
- The interrupted items came back after ___ s. Why that long:
- Why nothing was doubled (one sentence, in my own words):

### Dead-letter list

| Stage (parse / extract / download / gave up) | Items | What I did |
|---|---|---|
| | | |

### Live ingestion

- DjangoDesk on Render: ___ of 5 documents done, ___ failed. The reasons:
- A request without the token gets status ___

### Week 2 against Monday's estimate

- docs/CAPACITY.md said: ___ pages, ___ tokens. docs/INGEST_REPORT.md says: ___ pages, ___ tokens
- The difference, and why:

### One thing that went wrong today, and how I fixed it
