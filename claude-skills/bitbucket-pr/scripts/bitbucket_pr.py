#!/usr/bin/env python3
# Bitbucket Cloud pull request CLI for Claude Code.
#
# Credentials are read only from environment variables:
# - BITBUCKET_USERNAME + BITBUCKET_APP_PASSWORD for Basic auth
# - BITBUCKET_OAUTH_TOKEN for Bearer auth

from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_BASE = "https://api.bitbucket.org/2.0"
CONFIG_PATH = Path.home() / ".claude" / "bitbucket-pr" / "config.json"
DEFAULT_KEYCHAIN_SERVICE = "claude-bitbucket-app-password"


class BitbucketError(RuntimeError):
    pass


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BitbucketError(f"Invalid config JSON: {CONFIG_PATH}") from exc


def read_keychain_password(username: str, service: str) -> str | None:
    try:
        result = subprocess.run(
            ["/usr/bin/security", "find-generic-password", "-s", service, "-a", username, "-w"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    password = result.stdout.strip()
    return password or None


def read_configured_keychain_secret(config: dict[str, Any]) -> str | None:
    service = (
        os.environ.get("BITBUCKET_TOKEN_KEYCHAIN_SERVICE")
        or config.get("token_keychain_service")
        or config.get("keychain_service")
        or DEFAULT_KEYCHAIN_SERVICE
    )
    account = (
        os.environ.get("BITBUCKET_TOKEN_KEYCHAIN_ACCOUNT")
        or config.get("token_keychain_account")
        or config.get("username")
        or "bitbucket-api-token"
    )
    return read_keychain_password(account, service)


def basic_auth_header(username: str, password: str) -> dict[str, str]:
    raw = f"{username}:{password}".encode("utf-8")
    encoded = base64.b64encode(raw).decode("ascii")
    return {"Authorization": f"Basic {encoded}"}


def build_auth_headers() -> dict[str, str]:
    config = load_config()
    auth_type = config.get("auth_type")

    # Bitbucket Cloud API tokens are used as Basic auth password with the Atlassian account email.
    if auth_type in {"api_token_basic", "bitbucket_api_token"}:
        username = os.environ.get("BITBUCKET_USERNAME") or config.get("username")
        token = os.environ.get("BITBUCKET_API_TOKEN") or read_configured_keychain_secret(config)
        if username and token:
            return basic_auth_header(username, token)

    # OAuth access tokens use Bearer auth.
    token = os.environ.get("BITBUCKET_OAUTH_TOKEN") or config.get("oauth_token")
    if not token and auth_type in {"oauth_token", "bearer"}:
        token = read_configured_keychain_secret(config)
    if token:
        return {"Authorization": f"Bearer {token}"}

    # Legacy app password flow. App passwords are being removed by Bitbucket Cloud.
    username = os.environ.get("BITBUCKET_USERNAME") or config.get("username")
    app_password = os.environ.get("BITBUCKET_APP_PASSWORD")
    if not app_password and username:
        service = (
            os.environ.get("BITBUCKET_KEYCHAIN_SERVICE")
            or config.get("keychain_service")
            or DEFAULT_KEYCHAIN_SERVICE
        )
        app_password = read_keychain_password(username, service)

    if username and app_password:
        return basic_auth_header(username, app_password)

    raise BitbucketError(
        "Missing authentication. Configure auth_type=api_token_basic with username and a Keychain token, "
        "set BITBUCKET_OAUTH_TOKEN, or set BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD."
    )


def split_repo(repo: str) -> tuple[str, str]:
    parts = repo.strip().split("/")
    if len(parts) != 2 or not all(parts):
        raise BitbucketError("--repo must be in workspace/repo_slug form, e.g. kyobobook/product-llm-wiki")
    return parts[0], parts[1]


def build_ssl_context() -> ssl.SSLContext:
    ca_file = os.environ.get("BITBUCKET_CA_FILE")
    if ca_file:
        return ssl.create_default_context(cafile=ca_file)
    try:
        import certifi  # type: ignore
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    headers = {
        "Accept": "application/json",
        **build_auth_headers(),
    }
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(f"{API_BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30, context=build_ssl_context()) as resp:
            body = resp.read().decode("utf-8")
            if not body:
                return {}
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
            message = json.dumps(parsed, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            message = body
        raise BitbucketError(f"Bitbucket API {method} {path} failed: HTTP {exc.code}\n{message}") from exc
    except urllib.error.URLError as exc:
        raise BitbucketError(f"Bitbucket API request failed: {exc}") from exc


def pr_summary(pr: dict[str, Any]) -> dict[str, Any]:
    links = pr.get("links") or {}
    html = (links.get("html") or {}).get("href")
    source = (((pr.get("source") or {}).get("branch") or {}).get("name"))
    target = (((pr.get("destination") or {}).get("branch") or {}).get("name"))
    return {
        "id": pr.get("id"),
        "title": pr.get("title"),
        "state": pr.get("state"),
        "source": source,
        "target": target,
        "author": ((pr.get("author") or {}).get("display_name")),
        "url": html,
    }


def cmd_create(args: argparse.Namespace) -> dict[str, Any]:
    workspace, repo_slug = split_repo(args.repo)
    payload: dict[str, Any] = {
        "title": args.title,
        "source": {"branch": {"name": args.source}},
        "destination": {"branch": {"name": args.target}},
        "close_source_branch": args.close_source_branch,
    }
    if args.description:
        payload["description"] = args.description
    if args.reviewers:
        payload["reviewers"] = [{"uuid": r} for r in args.reviewers]

    pr = request("POST", f"/repositories/{workspace}/{repo_slug}/pullrequests", payload)
    return pr_summary(pr)


def cmd_get(args: argparse.Namespace) -> dict[str, Any]:
    workspace, repo_slug = split_repo(args.repo)
    pr = request("GET", f"/repositories/{workspace}/{repo_slug}/pullrequests/{args.pr}")
    return pr_summary(pr)


def cmd_merge(args: argparse.Namespace) -> dict[str, Any]:
    workspace, repo_slug = split_repo(args.repo)
    payload: dict[str, Any] = {
        "type": "pullrequest_merge_parameters",
        "merge_strategy": args.strategy,
        "close_source_branch": args.close_source_branch,
    }
    if args.message:
        payload["message"] = args.message
    pr = request("POST", f"/repositories/{workspace}/{repo_slug}/pullrequests/{args.pr}/merge", payload)
    return pr_summary(pr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bitbucket Cloud pull request CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a pull request")
    create.add_argument("--repo", required=True, help="workspace/repo_slug")
    create.add_argument("--source", required=True, help="source branch")
    create.add_argument("--target", required=True, help="target branch")
    create.add_argument("--title", required=True, help="pull request title")
    create.add_argument("--description", default="", help="pull request description")
    create.add_argument("--reviewers", nargs="*", help="reviewer UUIDs")
    create.add_argument("--close-source-branch", action="store_true", help="close source branch after merge")
    create.set_defaults(func=cmd_create)

    get = sub.add_parser("get", help="Show a pull request")
    get.add_argument("--repo", required=True, help="workspace/repo_slug")
    get.add_argument("--pr", required=True, type=int, help="pull request id")
    get.set_defaults(func=cmd_get)

    merge = sub.add_parser("merge", help="Merge a pull request")
    merge.add_argument("--repo", required=True, help="workspace/repo_slug")
    merge.add_argument("--pr", required=True, type=int, help="pull request id")
    merge.add_argument("--strategy", default="merge_commit", choices=["merge_commit", "squash", "fast_forward"], help="merge strategy")
    merge.add_argument("--message", default="", help="merge commit message")
    merge.add_argument("--close-source-branch", action="store_true", help="close source branch after merge")
    merge.set_defaults(func=cmd_merge)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = args.func(args)
    except BitbucketError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

