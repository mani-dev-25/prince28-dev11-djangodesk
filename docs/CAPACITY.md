# Capacity plan: DjangoDesk

Full corpus target: Docs for 3 versions + release notes + security notes (3,000+ pages)

<!-- generated:start -->
## Measured on my start corpus (2026-11-23 09:17 UTC)

| What | Value |
|---|---|
| Files | 793 |
| Size on disk | 25.2 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 5,425 |
| Characters of text | 11,478,938 |
| Estimated tokens (characters / 4) | 2,869,734 |
| Tokens per page | 529 |
| PDFs with almost no text (scanned? OCR is Day 7) | 0 |
| Files not measured (zip, xlsx, unreadable) | 83 |

## Estimate for the full corpus (target: 3,000 pages)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 0.6 |
| Tokens | measured tokens x scale | 1.59 M |
| Raw files | measured MB x scale | 14 MB |
| Chunks | tokens / 400 x 1.15 overlap | 4,562 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $0.27 = Rs 26 |
| Vector storage | chunks x 768 numbers x 4 bytes | 14 MB |
| Text in Postgres | characters x scale x 1.2 | 8 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->

## What I conclude

1. Is embedding cost a problem for this product? (1 line, with the number)
2. Do the vectors and text fit in my free Postgres? (1 line: compare with the storage limit on my database dashboard)
3. Which number above am I least sure about, and how will I measure it better? (1 line)
4. What changes if the corpus grows 10 times? (2 lines)
