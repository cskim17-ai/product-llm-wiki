---
name: llm-wiki-html-preview
description: Use when rendering product-llm-wiki markdown source or wiki files into readable Tailwind CSS based HTML previews, especially for reviewing sources/ documents before optional wiki reflection.
---

# LLM Wiki HTML Preview Skill

Use this skill in the `product-llm-wiki` repository when the user wants markdown documents, especially `sources/` files, rendered into readable HTML.

## Principle

- Keep `.md` files as the Source of Truth.
- Treat `schema.md` as the policy router and `docs/wiki-policy/html-preview.md` as the detailed rendering policy.
- Treat generated HTML as read-only preview output that may be committed and shared.
- Do not edit generated HTML by hand.
- Default output directory is `html-preview/`.
- Shared preview assets live under `html-preview/assets/`.
- Browser tab favicon is a shared asset at `html-preview/assets/kyobo-favicon.png`; individual HTML files only reference this common file from their `<head>`.
- The left HTML Preview navigation is generated as a shared `html-preview/assets/preview-nav.js`; individual HTML files load this common menu instead of embedding a static copy.
- Prefer rendering `sources/` first; rendering `wiki/` is also allowed.
- Wiki reflection is optional and must be requested separately or clearly implied.
- Do not read `.secrets`.

## Rendering Quality Bar

The preview should be pleasant enough for humans to inspect source documents directly, not merely a raw markdown dump.

- Use a collaborative-document style layout: top bar, document title, metadata panel, and a focused reading column.
- YAML front matter at the top of markdown files should not be rendered in the article body. Render it in the right document information panel as readable document metadata such as title, type, domain, created/updated author, dates, source origin, and wiki status.
- The repository partially adopts OKF metadata. When front matter includes `description`, `resource`, `tags`, or `timestamp`, surface those values in the metadata panel and use them for better document preview snippets. Do not add metadata directly to source markdown during rendering.
- The left document navigation and right metadata panel should be collapsible from the top bar; when a panel is closed, the reading column should naturally expand.
- Prioritize source readability over decorative styling.
- Tables must be easy to scan:
  - clear header contrast
  - comfortable cell padding
  - zebra rows
  - hover row emphasis
  - readable wrapping for long text, links, and inline code
  - horizontal scroll only when a table is truly wide
- Body text should use generous line-height and restrained heading scale.
- Code blocks should have strong contrast, preserve whitespace, show a language label, and apply renderer-side syntax highlighting for common languages such as SQL, Python, Bash, JSON/YAML, Java/Kotlin, and JS/TS.
- Inline code identifiers such as DB tables, procedures, API paths, Kafka topics, code values, and repository slugs should be progressively enhanced with lightweight hover context. The renderer builds `html-preview/assets/entity-index.js` from `sources/`, `wiki/`, and `templates/`, so repeated tables/procedures/topics can link to the best related HTML Preview document. Code expressions such as `sale_cdtn_code = '005'` should use Markdown table mappings to show the code value meaning and related document. Confirmed repository slugs may link to Bitbucket, but explicit Markdown links in source files remain preferred.
- Existing wiki/source/template document titles left as plain text or inline code should be progressively enhanced into internal document links. When the same title exists in multiple places, prefer `wiki`, then `sources`, then `templates`.
- Links and wiki links should be visually distinct without dominating the page.
- Do not introduce brand-specific styling unless the user explicitly asks and later confirms that direction.

## Common Requests

Natural language examples:

```text
이 source 문서 HTML로 보기 좋게 렌더링해줘
```

```text
sources/07-신규광고시스템-개발 하위 문서들 HTML preview 만들어줘
```

```text
이 HTML preview 보고 wiki 반영할지 판단해줘
```

## Workflow

1. Work from the repository root.
2. Identify the requested markdown file or directory under `sources/` or `wiki/`.
3. Run the bundled renderer:

```bash
python3 scripts/render_md_html.py <path>
```

4. For directory rendering, pass the directory path:

```bash
python3 scripts/render_md_html.py sources/07-신규광고시스템-개발
```

5. The script writes output under `html-preview/`, preserving the source-relative directory structure.
6. The script also updates shared assets, including `assets/kyobo-logo.png`, `assets/kyobo-favicon.png`, `assets/preview.css`, `assets/preview-page.js`, `assets/preview-nav.js`, and `assets/entity-index.js`.
7. Generated HTML is shareable, but should be regenerated from markdown instead of edited directly.
8. Report the generated HTML path to the user.
9. If the user also asks to reflect the source into wiki, use the `llm-wiki-ingest` workflow after preview generation.
10. If the output is visually poor, improve `scripts/render_md_html.py` template/CSS rather than asking the user to accept low-quality HTML.
11. Do not retrofit existing markdown files to satisfy OKF metadata during preview generation. Metadata cleanup belongs to the ingest/document-quality workflow.

## Options

Use `--out` only when the user asks for a different preview directory.

```bash
python3 scripts/render_md_html.py sources --out html-preview
```

Use `--open` only when the user explicitly asks to open the generated file and browser/tool approval is available.

## Validation

After adding or changing the skill, run:

```bash
python3 scripts/render_md_html.py --help
```

For a real smoke test, render one small markdown file and confirm the generated path exists.
