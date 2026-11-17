# DjangoDesk: Requirements

## Functional (what it does)

| ID | Requirement |
|----|-------------|
| F1 | Answer a Django question using retrieved documentation passages. |
| F2 | Every answer cites the doc page and Django version it came from. |
| F3 | For ORM questions, run the suggested code on a sample database and return the SQL and query count before and after. |
| F4 | When the docs do not contain the answer (like Q6), say so instead of guessing. |
| F5 | Let the user filter answers by Django LTS version. |

## Non-functional (how well it does it)

| ID | Requirement | Number |
|----|-------------|--------|
| N1 | Accuracy: ORM code answers run and reduce queries as claimed | 90% or more on 30 tasks |
| N2 | Speed: p95 answer time | 10 seconds or less |
| N3 | Speed: /health response time | 100 ms or less |
| N4 | Cost per answer | Rs. 2 or less |
| N5 | Security: secrets committed to the repo | 0 |
