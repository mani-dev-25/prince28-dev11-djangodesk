
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

### Rollback drill
A manual rollback procedure is documented. A full rollback drill was not performed yet.

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
