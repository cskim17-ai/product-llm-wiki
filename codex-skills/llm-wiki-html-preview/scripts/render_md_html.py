#!/usr/bin/env python3
"""Compatibility wrapper for the shared product-llm-wiki HTML renderer."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    shared_renderer = repo_root / "scripts" / "render_md_html.py"
    if not shared_renderer.exists():
        sys.stderr.write(f"Shared renderer not found: {shared_renderer}\n")
        sys.exit(1)
    runpy.run_path(str(shared_renderer), run_name="__main__")


if __name__ == "__main__":
    main()
