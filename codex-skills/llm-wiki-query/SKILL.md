---
name: llm-wiki-query
description: Use for product-llm-wiki repository questions, searches, knowledge lookup, operational/process questions, or when asked what exists in the wiki. Answers must use wiki/ as the primary Source of Truth and sources/ only for verification or wiki omission detection.
---

# LLM Wiki Query Skill

Use this skill when working in a `product-llm-wiki` repository, or when the current workspace contains `schema.md`, `index.md`, `wiki/`, `sources/`, and `scripts/wiki-search`.

## Query Principle

- Answer from `wiki/` first.
- Treat `schema.md` as the policy router. For query behavior, use `docs/wiki-policy/query.md`; for entity hover/link meaning, use `docs/wiki-policy/entities.md`; for preview link behavior, use `docs/wiki-policy/html-preview.md`.
- Use `index.md` and `topic-map.yml` to locate relevant wiki pages.
- Use `sources/` only for verification, detailed history, source traceability, or when the wiki appears incomplete.
- If the answer exists only in `sources/`, state that the wiki is missing or incomplete for that point.
- Do not make `sources/` the first-class answer base for ordinary questions.
- When a document has OKF-compatible front matter, use `title`, `description`, `resource`, `tags`, and `timestamp` to judge relevance and freshness, but verify the answer from the markdown body and citations/source links.

## Workflow

1. Work from the repository root. If needed, locate it by finding `schema.md`, `index.md`, `wiki/`, `sources/`, and `scripts/wiki-search`.
2. Search `index.md`, `topic-map.yml`, `wiki/entities`, and `wiki/topics` first.
3. If `scripts/wiki-search` is available and qmd has been initialized, prefer it for discovery:
   - `scripts/wiki-search search --with-preview --graph "<query>"` for wiki-only search plus graph-expanded related documents with an `open:` link that points to HTML Preview when generated, or markdown when not generated
   - `scripts/wiki-search source-search --with-preview --graph "<query>"` only for source verification or wiki omission checks, using the same `open:` link preference
   - `scripts/wiki-search all-search --with-preview --graph "<query>"` when the user explicitly asks to include both wiki and sources
   - `scripts/wiki-search get <qmd-uri-or-docid>` to read a result
4. If qmd is unavailable or returns insufficient results, use `scripts/wiki-search graph --with-preview "<query>"` and `rg -n "keyword" index.md topic-map.yml wiki` as fallback and cite the matching `html-preview/{path-with-html-extension}` when it exists; otherwise cite the markdown file.
5. Read the most relevant wiki files before answering.
6. If wiki coverage is insufficient, search `sources/` to verify whether source material exists.
7. When using source-only facts, mark them as source-derived and identify the missing wiki coverage.
8. If the user asks to update or maintain the wiki, switch to the ingest workflow and update source/wiki/mapping/index/log files.
9. Keep answers concise and operational: cause, check query/procedure, action, and caveat.
10. When useful, cite Obsidian wikilinks, the preferred open link, and the source markdown path.
11. Unless the user asks not to record it, log meaningful query/answer interactions with `scripts/conversation-log.py` so future answer quality can be reviewed.

## Graph Expansion

`scripts/wiki-search --graph` uses `sync/wiki-graph.json`, generated from repository-owned markdown links and metadata.

- It does not use `.obsidian/graph.json`; that file is only Obsidian UI state.
- Refresh graph data with `scripts/wiki-search graph-update`.
- Use graph results as candidates only. Always open and verify the selected wiki files before answering.
- Graph expansion is useful when qmd finds a nearby hub page but the actual answer is in a linked child page, source mapping, or entity page.

## Conversation Logging

Use conversation logging for repository knowledge questions, operational/process lookups, and answers that identify wiki gaps.

- Store logs under `conversations/YYYY-Www.md`.
- Do not store names, account identifiers, email addresses, or branch names in query/conversation logs.
- Local Git `user.name` based author metadata is only for ingest-created or meaningfully updated `sources/` and `wiki/` front matter.
- Record the question, final answer or faithful answer summary, answer basis (`wiki`, `sources`, `mixed`, `meta`, or `unknown`), domain, cited documents, tags, and whether wiki coverage was missing.
- Do not store passwords, tokens, secrets, or sensitive personal data in raw form. Summarize or mask them.
- If the answer is source-only, pass `--wiki-gap`.
- If repeated questions expose missing `description`, `resource`, tags, citations, or entity links, mention that as a wiki quality gap rather than silently relying on weak metadata.

Example:

```bash
python3 scripts/conversation-log.py \
  --query "상품추천 에이전트 topic 구분 코드 찾아줘" \
  --answer-file /tmp/llm-wiki-answer.md \
  --basis wiki \
  --domain "08-AI상품추천-에이전트" \
  --source "wiki/topics/08-AI상품추천-에이전트/..." \
  --tag topic-code
```

## Status Checks

- Run `python3 scripts/sync-status.py` when asked about wiki reflection status or after wiki edits.
- Use `wiki-map.yml` for source sync status.
- Use `topic-map.yml` for topic classification status.

## Git

Do not commit or push unless the user explicitly asks.
