# Codex Skills

이 디렉토리는 `product-llm-wiki` 작업용 Codex 스킬 공유본입니다.

Claude Code용 스킬은 이 디렉토리를 그대로 복사하지 않고, `claude-skills/` 하위의 별도 공유본을 사용합니다.

## 설치 방법

필요한 스킬 디렉토리를 개인 Codex 스킬 디렉토리로 복사합니다.

```bash
cp -R codex-skills/llm-wiki-ingest ~/.codex/skills/
cp -R codex-skills/llm-wiki-query ~/.codex/skills/
cp -R codex-skills/llm-wiki-html-preview ~/.codex/skills/
cp -R codex-skills/bitbucket-pr ~/.codex/skills/
```

## 업데이트 동기화

`codex-skills/` 하위 스킬을 수정한 경우, 이미 `~/.codex/skills/`에 복사된 스킬은 자동으로 갱신되지 않습니다. 수정 후에는 사용하는 스킬을 다시 동기화합니다.

```bash
rsync -a --delete codex-skills/llm-wiki-ingest/ ~/.codex/skills/llm-wiki-ingest/
rsync -a --delete codex-skills/llm-wiki-query/ ~/.codex/skills/llm-wiki-query/
rsync -a --delete codex-skills/llm-wiki-html-preview/ ~/.codex/skills/llm-wiki-html-preview/
```

동기화 후 LLM Wiki 스킬의 공통 파일 드리프트를 확인합니다.

```bash
python3 scripts/check-skill-sync.py
```

HTML Preview 렌더러의 실제 구현은 `scripts/render_md_html.py`에서 관리합니다. 이 디렉토리의 `llm-wiki-html-preview/scripts/render_md_html.py`는 기존 스킬 호출 호환을 위한 wrapper입니다.

## 스킬 목록

- `llm-wiki-ingest`: Loop, Planner, 운영 문의, 개발 건 등 원본 문서를 `sources/`에 입력하고 `wiki/`로 반영할 때 사용합니다.
- `llm-wiki-query`: 위키 질의 시 `wiki/`를 우선 검색하고 `sources/`는 검증 또는 누락 확인 용도로 사용할 때 사용합니다.
- `llm-wiki-html-preview`: `sources/` 또는 `wiki/`의 markdown 문서를 `html-preview/` 하위 Tailwind CSS 기반 HTML 미리보기로 렌더링할 때 사용합니다.
- `bitbucket-pr`: 브라우저 UI 없이 Bitbucket Cloud PR 생성, 조회, 머지를 처리할 때 사용합니다.
