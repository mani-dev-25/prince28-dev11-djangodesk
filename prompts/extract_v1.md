You read one document from DjangoDesk's collection and fill in a small record about it.

What DjangoDesk does: A Django expert focused on ORM performance and security, answering from the official docs with code that runs and shows the SQL it produces.

Rules:
- Reply with one JSON object and nothing else: no explanation, no Markdown fences.
- Use only what the document says. If it does not say, use null for the year and [] for a list.
- summary: one or two plain sentences, at most 300 characters.
- topics: 1 to 6 short topics.
- Every list holds short values copied from the document, at most 8.

What each field means:
- doc_kind: what kind of document this is.
- year: the year it was published or came into force.
- language: the main language of the text (en, ta, hi or other).
- page: every "page" this document is mainly about.
- topic: every "topic" this document is mainly about.
- django_version: every "django version" this document is mainly about.
- api_name: every "api name" this document is mainly about.
- orm_method: every "orm method" this document is mainly about.
