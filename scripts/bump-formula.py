#!/usr/bin/env python3
"""更新 Homebrew formula 的 version / url / sha256，并可选提交。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMULA_DIR = ROOT / "Formula"

FORMULAS: dict[str, tuple[str, str]] = {
    "senv": ("solo-kingdom/senv", "main"),
    "llmwiki": ("solo-kingdom/llmwiki", "main"),
    "transit": ("solo-kingdom/transit", "main"),
    "grepom": ("sunzhenkai/grepom", "master"),
    "mdserve": ("sunzhenkai/mdserve", "main"),
}


def log(msg: str) -> None:
    print(f"=> {msg}")


def die(msg: str) -> None:
    print(f"错误: {msg}", file=sys.stderr)
    sys.exit(1)


def github_api(path: str) -> object:
    req = urllib.request.Request(
        f"https://api.github.com/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "solo-kingdom-homebrew-tap-bump",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def resolve_ref(repo: str, branch: str, explicit_ref: str | None) -> str:
    if explicit_ref:
        return explicit_ref

    try:
        release = github_api(f"repos/{repo}/releases/latest")
        tag = release.get("tag_name")
        if tag:
            return tag
    except Exception:
        pass

    tags = github_api(f"repos/{repo}/tags?per_page=1")
    if tags:
        return tags[0]["name"]

    commit = github_api(f"repos/{repo}/commits/{branch}")
    return commit["sha"]


def normalize_version(raw: str) -> str:
    return raw.removeprefix("v").removeprefix("V")


def resolve_version(explicit: str | None, ref: str) -> str | None:
    if explicit:
        return explicit
    if re.match(r"^v?[0-9]", ref):
        return normalize_version(ref)
    return None


def download_sha256(url: str) -> str:
    with urllib.request.urlopen(url) as resp:
        data = resp.read()
    return hashlib.sha256(data).hexdigest()


def read_current_version(formula_file: Path) -> str:
    match = re.search(r'^  version "(.*)"$', formula_file.read_text(), re.M)
    if not match:
        die(f"无法读取版本: {formula_file}")
    return match.group(1)


def update_formula_file(
    formula: str,
    formula_file: Path,
    url: str,
    version: str,
    sha256: str,
    ref: str,
) -> None:
    content = formula_file.read_text()
    content = re.sub(r'^  url ".*"$', f'  url "{url}"', content, count=1, flags=re.M)
    content = re.sub(r'^  version ".*"$', f'  version "{version}"', content, count=1, flags=re.M)
    content = re.sub(r'^  sha256 ".*"$', f'  sha256 "{sha256}"', content, count=1, flags=re.M)

    if formula == "llmwiki":
        short_ref = ref[:7]
        content = re.sub(
            r"-X main\.Commit=[^\s\"]+",
            f"-X main.Commit={short_ref}",
            content,
            count=1,
        )

    formula_file.write_text(content)


def bump_one(
    formula: str,
    explicit_version: str | None,
    explicit_ref: str | None,
    dry_run: bool,
) -> Path:
    if formula not in FORMULAS:
        die(f"未知 formula: {formula}")

    repo, branch = FORMULAS[formula]
    formula_file = FORMULA_DIR / f"{formula}.rb"
    if not formula_file.is_file():
        die(f"找不到 formula 文件: {formula_file}")

    log(f"处理 {formula} ({repo})")

    ref = resolve_ref(repo, branch, explicit_ref)
    version = resolve_version(explicit_version, ref)
    if not version:
        version = read_current_version(formula_file)
        log(f"{formula}: 未提供版本且 ref 非 tag，保留当前版本 {version}")

    url = f"https://github.com/{repo}/archive/{ref}.tar.gz"
    log(f"下载 {url}")
    sha256 = download_sha256(url)
    log(f"{formula}: version={version} ref={ref} sha256={sha256[:12]}...")

    if dry_run:
        log(f"[dry-run] 将更新 {formula_file}")
        return formula_file

    update_formula_file(formula, formula_file, url, version, sha256, ref)
    log(f"已更新 {formula_file}")
    return formula_file


def git_commit(changed: list[Path], formulas: list[str]) -> None:
    rel_paths = [str(p.relative_to(ROOT)) for p in changed]
    diff = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--quiet", "--", *rel_paths],
        check=False,
    )
    if diff.returncode == 0:
        log("没有变更，跳过提交")
        return

    subprocess.run(["git", "-C", str(ROOT), "add", "--", *rel_paths], check=True)

    if len(formulas) == 1:
        version = read_current_version(FORMULA_DIR / f"{formulas[0]}.rb")
        msg = f"bump {formulas[0]} to {version}"
    else:
        msg = f"bump formulas: {' '.join(formulas)}"

    subprocess.run(["git", "-C", str(ROOT), "commit", "-m", msg], check=True)
    log(f"已提交: {msg}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="更新 Homebrew formula 版本并提交",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  scripts/bump-formula.py senv --ref v0.2.0
  scripts/bump-formula.py llmwiki --version 0.2.0 --ref abc1234
  scripts/bump-formula.py --all --no-commit
""",
    )
    parser.add_argument("formulas", nargs="*", help="formula 名称")
    parser.add_argument("--all", action="store_true", help="更新所有 formula")
    parser.add_argument("--version", help="指定 formula 版本")
    parser.add_argument("--ref", help="指定 git tag 或 commit")
    parser.add_argument("--no-commit", action="store_true", help="不创建 git commit")
    parser.add_argument("--dry-run", action="store_true", help="预览变更，不写文件")
    args = parser.parse_args()

    if args.all:
        formulas = list(FORMULAS)
    else:
        formulas = args.formulas

    if not formulas:
        parser.print_help()
        sys.exit(1)

    changed: list[Path] = []
    for formula in formulas:
        changed.append(
            bump_one(formula, args.version, args.ref, args.dry_run)
        )

    if args.dry_run or args.no_commit:
        return

    git_commit(changed, formulas)


if __name__ == "__main__":
    main()
