---
name: llm-wiki-ingest
description: Use when adding Loop, Planner, operational inquiry, development notes, guides, or raw source content to the product-llm-wiki repository and reflecting it into wiki topics/entities with mapping files.
---

# LLM Wiki Ingest Skill

Use this skill when working in a `product-llm-wiki` repository, or when the current workspace contains `schema.md`, `index.md`, `wiki/`, `sources/`, and `scripts/wiki-search`.

## Source of Truth

- Read `schema.md` first as the policy router, then read the relevant detailed policy files:
  - `docs/wiki-policy/ingest.md` for source input, naming, front matter, images, imports, and related links.
  - `docs/wiki-policy/structure.md` for domain and directory placement.
  - `docs/wiki-policy/wiki-sync.md` for wiki reflection, mapping, index, and log completion criteria.
  - `docs/wiki-policy/entities.md` for DB/API/Kafka/Repository entity work.
  - `docs/wiki-policy/okf.md` for OKF metadata rules.
  - `docs/wiki-policy/html-preview.md` for preview completion and rendering behavior.
- Read `AGENTS.md` for execution guidance only.
- Use `wiki-map.yml` for source-to-wiki sync state.
- Use `topic-map.yml` for topic classification.
- Use `templates/` when the input is a development or operational write-up.
- Never read `.secrets`.

## Workflow

1. Work from the repository root. If needed, locate it by finding `schema.md`, `index.md`, `wiki/`, `sources/`, and `scripts/wiki-search`.
2. Classify the content by domain using `schema.md`, `docs/wiki-policy/structure.md`, and existing `sources/` / `wiki/topics/` structure.
3. Save raw user-provided content under the correct `sources/{domain}/...` directory.
4. Use title-based Korean kebab-case filenames. Keep English acronyms or system names when they are the natural title.
5. Add YAML front matter to every created or meaningfully updated `sources/` and `wiki/` markdown file. Follow the repository's partial OKF adoption rule: include `type` and `title`, and add `description`, `resource`, `tags`, and `timestamp` when the values can be stated without guessing. Use local `git config user.name` for `created_by` / `updated_by`, and use `YYYY-MM-DD` dates. Do not write email addresses, tokens, or secret values into front matter.
6. Do not use `README.md` for source pages.
7. Preserve raw facts, links, IDs, SQL, tables, dates, and names. Do not invent missing details.
8. While preserving the original meaning, normalize the markdown so it renders well in HTML Preview. Follow the "Markdown authoring rules" below.
9. For development write-ups, follow `templates/개발건-정리.md`.
10. For operational write-ups, follow `templates/운영정리건-정리.md` when present.
11. Reflect reusable knowledge into `wiki/topics/{domain}/...` or `wiki/entities/...`.
12. Wiki files should be concise, query-friendly, and structured around reusable facts, procedures, causes, checks, and decisions.
13. Add a `## 출처` section with relative links to source files.
14. Prefer wiki links between wiki pages. Avoid turning source files into graph navigation pages.
15. Update `index.md` when wiki pages are added, removed, or renamed.
16. Update `topic-map.yml` when topic files are added, renamed, reclassified, or status changes.
17. Update `wiki-map.yml` for source sync state: synced, integrated, deferred, archived, or omitted according to `docs/wiki-policy/wiki-sync.md`.
18. Generate HTML Preview for every markdown file created or meaningfully updated during ingest.
19. Add one concise line to the current monthly log file (`logs/YYYY-MM.md`) for every meaningful source/wiki/mapping/preview change. Keep root `log.md` as the monthly log index only.
20. Run `python3 scripts/sync-status.py` and resolve reported issues.
21. Check unresolved wiki links before finishing.

When PDFs, XLSX files, or other raw evidence files are placed under `sync/imports/`, run `python3 scripts/import-link-audit.py --write` to produce `sync/import-links.md`. Treat the result as review candidates only. Do not automatically mutate source documents just because a filename is similar.

When a document has link-like sections such as `관련 링크`, `문서 및 링크`, `참고 문서`, `문서 목록`, Loop, Planner, or Confluence references, do not leave plain text filenames unexamined. Search existing `sources/`, `wiki/`, `templates/`, and `sync/imports/` for reliable matching documents and prefer explicit Markdown links. For existing documents, run `python3 scripts/related-link-audit.py --write` to produce `sync/related-link-candidates.md`; treat the result as review candidates only and apply only high-confidence matches.

When asked to create wiki/spec documents from existing repeated data, run `python3 scripts/entity-doc-audit.py --write` to produce `sync/entity-doc-candidates.md`. Treat the result as candidates only. Create or enrich docs from high-confidence repeated DB tables, procedures, API paths, Kafka topics, and repository references. Prefer enriching an existing wiki/spec when the candidate already has wiki coverage, and update maps, index, log, and previews only for documents actually changed.
For repeated DB tables/views/sequences/procedures, do not stop at a terse hover description. If the source gives enough evidence, create or enrich a DB object entity under `wiki/entities/db/` using `templates/DB-객체-명세.md`. A useful DB object document should identify the database/schema/object, Korean table/business name, columns, code columns and code values, programs or pipelines that use it, related objects, operational impact, and source links. DB object docs and HTML Preview hover summaries should lead with the Korean table/business name and how the object is used in actual work, not merely the raw identifier. DB object entity filenames and H1 titles must use the schema-less object base name, such as `t_ra_qa_vltn_r`, not a schema-qualified name such as `dev.t_ra_qa_vltn_r`; schema-qualified names belong in the document body as confirmed schema-specific objects.

## Markdown Authoring Rules

Use markdown that is stable for both humans and the HTML Preview renderer.

- Use one `#` title that matches the page title, then use `##` and `###` for sections. Avoid skipping heading levels when possible.
- Start created or meaningfully updated markdown files with YAML front matter. HTML Preview renders this metadata in the document information panel, not in the article body.
  - Required OKF-compatible fields for new or meaningfully updated documents: `type`, `title`.
  - Recommended OKF-compatible fields: `description`, `resource`, `tags`, `timestamp`.
  - Minimal source example: `title`, `type: source`, `description`, `domain`, `resource`, `tags`, `timestamp`, `created_by`, `created_at`, `updated_by`, `updated_at`, `wiki_status`.
  - Minimal wiki example: `title`, `type: wiki`, `description`, `domain`, `resource`, `tags`, `timestamp`, `created_by`, `created_at`, `updated_by`, `updated_at`, `sources`.
  - Preserve existing `created_by` and `created_at` when updating an existing document; update only `updated_by` and `updated_at`.
  - Do not retrofit existing documents only to satisfy OKF metadata unless the user explicitly asks for metadata/document quality cleanup.
- Decide the `#` title and filename by considering the parent category, pasted title, and file content together.
  - Keep the original title when it is already specific and consistent with the body.
  - Otherwise, make the title describe the actual development item, operational issue, design topic, or guide purpose, not just the parent category.
  - Prefer `교보문고 ai.txt, llms.txt 개발` over a generic category title such as `상품 AI`.
  - If pasted source text has a category-like title or the body summary describes a more specific work item, use the body summary or actual work item as the title.
- Convert structured lists from pasted text into pipe tables when comparison, status, owners, dates, API lists, DB columns, test cases, or WBS items are involved.
- Use fenced code blocks with a language label for SQL, JSON, shell, Python, Java, Kotlin, YAML, Mermaid, and logs.
  - SQL: ` ```sql `
  - shell commands: ` ```bash `
  - Mermaid diagrams: ` ```mermaid `
- Use Mermaid for flows, dependencies, architecture, sequence diagrams, or DAGs when the input describes a process that is easier to read visually.
- Save images under a nearby repository `assets/` directory and reference them with relative markdown image syntax: `![설명](assets/file.png)`.
  - Do not reference temporary pasted-image paths such as `/var/folders/...`, `/tmp/...`, or `file:///Users/...` directly in markdown.
  - Copy pasted/attached screenshots into the repository before linking them, and use useful alt text that describes the screenshot or diagram.
  - When the user asks to add an image to an existing page, update the target `sources/` or `wiki/` markdown with a real image link. Do not replace the image with a note such as `이미지 파일: xxx.png` or `동일 디렉토리 보관`.
  - If a source page and a wiki page represent the same content, decide whether the image belongs in the source, the wiki, or both. When the user does not specify, update the page they are viewing/requesting and check whether the paired page should also be updated.
  - After adding an image, render the changed markdown and verify that the generated HTML contains an `<img>` element for that image.
- Use task lists for checklists: `- [ ]` and `- [x]`.
- Use callouts for important notes:
  - `> [!NOTE]` for neutral notes.
  - `> [!TIP]` for recommendations.
  - `> [!WARNING]` for operational risk, deployment caution, or destructive work.
  - `> [!IMPORTANT]` for decisions or must-follow rules.
- Use horizontal rules `---` only to split major sections, not after every paragraph.
- Use inline code for identifiers such as table names, procedure names, API paths, Kafka topics, code values, env vars, commands, class names, and config keys.
  - The HTML Preview renderer progressively enhances some inline code identifiers with hover context, so preserve meaningful identifiers as inline code when they are not links.
  - If a table/procedure/topic is repeatedly referenced and carries reusable meaning, consider creating or linking a wiki/entity/detail document rather than leaving every occurrence as plain inline code.
  - For DB objects, capture nearby context such as DB/schema, column definitions, code values, source/sink topic, batch/API/program usage, and change impact so a later `wiki/entities/db/` document can be created without re-reading every source.
- Use markdown links for external/internal references. Use relative paths for repository files.
  - If the text points to an existing repository document or file, write it as a markdown link instead of plain inline code.
  - Example: `[상시-모니터링.md](상시-모니터링.md)`, not `` `상시-모니터링.md` ``.
  - Use inline code for filenames only when the filename is being discussed as a literal identifier and should not navigate anywhere.
  - If a phrase is an existing wiki/source/template document title, prefer a Markdown link instead of repeated plain text. Examples: `상품 데이터 모니터링 리스트`, `다. 시스템 모니터링`, `[템플릿] 개발, 테스트, 배포 시 체크리스트`.
  - In link-like sections (`관련 링크`, `문서 및 링크`, `참고 문서`, `문서 목록`, Loop/Planner/Confluence), convert plain text `.loop`, `.pptx`, `.xlsx`, `.pdf`, `.html`, or existing document names to Markdown links when a reliable repository match exists.
  - The HTML Preview renderer can auto-link plain text or inline code that exactly matches a known document title, but explicit Markdown links in source files remain preferred.
  - If a Bitbucket repository slug is confirmed, link it with `https://bitbucket.org/kyobobook/{repo-slug}/src/main/`.
  - If source text includes both `kyobobook/{repo-slug}` and its Bitbucket URL, collapse them into one markdown link on the slug text instead of repeating the URL on a separate line.
  - If a branch is explicit, use that branch URL, for example `https://bitbucket.org/kyobobook/python-batch/src/development/`.
  - For Bitbucket repository links, do not put inline code backticks inside the link text because the HTML Preview renderer treats that poorly.
  - Do not automatically treat `*-dev`, `*-prd`, pod names, hostnames, or Jenkins view names as Bitbucket repositories. Link them only when a reliable repository mapping is known.
- In `sources/`, preserve raw facts and source context first. In `wiki/`, rewrite into reusable knowledge.
- Do not store passwords, tokens, secret values, personal sensitive information, or raw credentials. Replace with a safe note such as `담당자 문의` or `마스킹`.
- Avoid raw HTML unless there is no markdown equivalent. Prefer markdown features supported by the renderer.

## HTML Preview Supported Syntax

When creating markdown, prefer these constructs because the shared HTML Preview renderer supports them:

| Markdown | Use for |
| --- | --- |
| `#`, `##`, `###` | Document title and section hierarchy |
| Pipe tables | Requirements, test cases, DB columns, schedules, status tables |
| Fenced code blocks | SQL, logs, JSON, shell commands, source snippets |
| ` ```mermaid ` | Flowcharts, sequence diagrams, DAGs, architecture sketches |
| `![alt](path)` | Local screenshots and diagrams |
| `- [ ]`, `- [x]` | Checklists |
| `> [!NOTE]`, `> [!WARNING]` | Callouts |
| `> quote` | Quoted source context or important excerpt |
| Nested ordered/unordered lists | Hierarchical notes |
| `---` | Major visual divider |
| `~~text~~` | Deprecated or removed item |
| `\|` inside tables | Literal pipe character in table cells |

If the input has ambiguous structure, choose the representation that will make later query and HTML preview reading easiest.

## HTML Preview Requirement

HTML Preview generation is part of ingest completion because users often review newly entered content visually.

- After creating or updating markdown under `sources/`, `wiki/`, `templates/`, or root metadata, run the shared renderer for the changed markdown path:

```bash
python3 scripts/render_md_html.py "sources/도메인/문서.md"
```

- If multiple related files changed, render each changed path or render the smallest containing directory.
- Do not treat a renderer failure as a reason to discard the markdown source. Keep the markdown, fix the render issue if it is local and obvious, and record unresolved preview failures in the current monthly log file (`logs/YYYY-MM.md`) or the final response.
- When a page has a generated HTML Preview, search/query answers should prefer showing the HTML Preview link for reading and keep the markdown path as the source reference.
- For image-heavy input, save images to a nearby `assets/` directory before rendering so the HTML page can display them immediately.

## Completion Check

A source is wiki-reflected only when the reusable knowledge is findable from `index.md` or `topic-map.yml`, mapped in `wiki-map.yml`, has an HTML Preview generated for changed markdown, and passes `scripts/sync-status.py` without issues.

## Git

Do not commit or push unless the user explicitly asks.
