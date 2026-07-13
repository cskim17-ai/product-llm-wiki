# Claude Code Skills

이 디렉토리는 `product-llm-wiki` 작업용 Claude Code 스킬 공유본입니다.
`codex-skills/`의 Claude Code 대응본이며, 같은 스킬을 Claude Code 환경에 맞게 보정해 두었습니다.

Codex용 스킬은 이 디렉토리를 사용하지 않고, `codex-skills/` 하위의 별도 공유본을 사용합니다.

## 설치 방법

필요한 스킬 디렉토리를 Claude Code 스킬 디렉토리로 복사합니다.

- 프로젝트 전용: 현재 레포의 `.claude/skills/`
- 사용자 전역: `~/.claude/skills/`

```bash
# 프로젝트 전용 (현재 레포에서 바로 사용)
cp -R claude-skills/llm-wiki-ingest .claude/skills/
cp -R claude-skills/llm-wiki-query .claude/skills/
cp -R claude-skills/llm-wiki-html-preview .claude/skills/
cp -R claude-skills/bitbucket-pr .claude/skills/

# 사용자 전역 (모든 레포에서 사용)
cp -R claude-skills/llm-wiki-ingest ~/.claude/skills/
cp -R claude-skills/llm-wiki-query ~/.claude/skills/
cp -R claude-skills/llm-wiki-html-preview ~/.claude/skills/
cp -R claude-skills/bitbucket-pr ~/.claude/skills/
```

> 이 레포의 `.claude/skills/`에는 위 4개 스킬이 이미 설치되어 있어, 현재 레포에서는 추가 복사 없이 바로 사용할 수 있습니다.

## 업데이트 동기화

`claude-skills/` 하위 스킬을 수정한 경우, 이미 `.claude/skills/` 또는 `~/.claude/skills/`에 복사된 스킬은 자동으로 갱신되지 않습니다. 수정 후에는 사용하는 스킬 디렉토리와 다시 동기화합니다.

프로젝트 전용 동기화:

```bash
rsync -a --delete claude-skills/llm-wiki-ingest/ .claude/skills/llm-wiki-ingest/
rsync -a --delete claude-skills/llm-wiki-query/ .claude/skills/llm-wiki-query/
rsync -a --delete claude-skills/llm-wiki-html-preview/ .claude/skills/llm-wiki-html-preview/
```

사용자 전역 동기화:

```bash
rsync -a --delete claude-skills/llm-wiki-ingest/ ~/.claude/skills/llm-wiki-ingest/
rsync -a --delete claude-skills/llm-wiki-query/ ~/.claude/skills/llm-wiki-query/
rsync -a --delete claude-skills/llm-wiki-html-preview/ ~/.claude/skills/llm-wiki-html-preview/
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

## codex-skills와의 차이

`codex-skills/`의 동일 스킬을 Claude Code 환경에 맞게 다음과 같이 보정했습니다.

- `bitbucket-pr`: 본문/스크립트의 `Codex` 표현을 `Claude Code`로, 설정 경로 `~/.codex/bitbucket-pr/` → `~/.claude/bitbucket-pr/`, Keychain 기본 라벨 `codex-bitbucket-app-password` → `claude-bitbucket-app-password`, 샌드박스 안내 `sandbox_permissions="require_escalated"` → `dangerouslyDisableSandbox: true`로 변경. (레거시 설치 마이그레이션 안내로 `codex-…` 라벨 언급은 일부 유지)
- `llm-wiki-html-preview`: 현재는 공통 렌더러 `scripts/render_md_html.py`를 호출하므로 Codex용 스킬과 핵심 동작을 동일하게 유지.
- `llm-wiki-ingest`, `llm-wiki-query`: 내용 동일(보정 불필요).
