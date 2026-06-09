#!/usr/bin/env python3
"""更新 Homebrew formula 的 version / url / sha256，并可选提交。

当上游默认分支有新 commit 且 HEAD 没有 semver tag 时，自动递增 patch 版本，
通过 SSH 在上游仓库创建并推送 tag，再更新 formula。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
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

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def log(msg: str) -> None:
    print(f"=> {msg}")


def die(msg: str) -> None:
    print(f"错误: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str], *, cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=capture,
    )


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


def ssh_remote(repo: str) -> str:
    return f"git@github.com:{repo}.git"


def normalize_version(raw: str) -> str:
    return raw.removeprefix("v").removeprefix("V")


def parse_semver(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(normalize_version(version))
    if not match:
        die(f"无法解析 semver 版本: {version}")
    return tuple(int(part) for part in match.groups())


def format_semver(parts: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in parts)


def max_semver(*versions: str) -> str:
    return format_semver(max(parse_semver(version) for version in versions))


def increment_patch(version: str) -> str:
    major, minor, patch = parse_semver(version)
    return f"{major}.{minor}.{patch + 1}"


def is_commit_ref(ref: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{7,40}", ref, re.I))


def is_semver_tag(ref: str) -> bool:
    return bool(SEMVER_RE.match(normalize_version(ref)))


def get_branch_head(repo: str, branch: str) -> str:
    commit = github_api(f"repos/{repo}/commits/{branch}")
    return commit["sha"]


def list_repo_tags(repo: str) -> list[dict[str, str]]:
    tags: list[dict[str, str]] = []
    page = 1
    while True:
        batch = github_api(f"repos/{repo}/tags?per_page=100&page={page}")
        if not batch:
            break
        tags.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return tags


def tags_on_commit(repo: str, commit: str) -> list[str]:
    tag_names = {
        tag["name"]
        for tag in list_repo_tags(repo)
        if tag["commit"]["sha"] == commit
    }
    tag_names.update(remote_tags_on_commit(repo, commit))
    return sorted(tag_names)


def remote_tags_on_commit(repo: str, commit: str) -> list[str]:
    result = run(["git", "ls-remote", "--tags", ssh_remote(repo)], capture=True)
    tags: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        sha, ref = line.split("\t")
        if not ref.startswith("refs/tags/"):
            continue
        tag = ref.removeprefix("refs/tags/")
        if tag.endswith("^{}"):
            continue
        if sha == commit:
            tags.append(tag)
    return tags


def latest_semver_tag_version(repo: str) -> str | None:
    versions: list[str] = []
    for tag in list_repo_tags(repo):
        normalized = normalize_version(tag["name"])
        if SEMVER_RE.match(normalized):
            versions.append(normalized)
    if not versions:
        return None
    return max_semver(*versions)


def best_semver_tag_on_commit(repo: str, commit: str) -> str | None:
    semver_tags = [
        tag for tag in tags_on_commit(repo, commit) if is_semver_tag(tag)
    ]
    if not semver_tags:
        return None
    return max(semver_tags, key=lambda tag: parse_semver(tag))


def remote_tag_commit(repo: str, tag: str) -> str | None:
    result = run(
        ["git", "ls-remote", ssh_remote(repo), f"refs/tags/{tag}"],
        capture=True,
    )
    line = result.stdout.strip()
    if not line:
        return None
    return line.split()[0]


def push_tag_ssh(repo: str, branch: str, commit: str, tag: str) -> None:
    existing = remote_tag_commit(repo, tag)
    if existing:
        if existing == commit:
            log(f"{repo}: 远程已存在 tag {tag}，跳过推送")
            return
        die(f"{repo}: tag {tag} 已指向其他 commit ({existing[:7]})")

    with tempfile.TemporaryDirectory() as tmp:
        repo_dir = Path(tmp) / "repo"
        run(["git", "clone", "--branch", branch, ssh_remote(repo), str(repo_dir)])
        head = run(["git", "rev-parse", "HEAD"], cwd=repo_dir, capture=True).stdout.strip()
        if head != commit:
            die(
                f"{repo}: 分支 {branch} HEAD ({head[:7]}) 与目标 commit ({commit[:7]}) 不一致"
            )
        run(["git", "tag", tag], cwd=repo_dir)
        run(["git", "push", "origin", tag], cwd=repo_dir)

    log(f"{repo}: 已通过 SSH 推送 tag {tag} -> {commit[:7]}")


def read_current_version(formula_file: Path) -> str:
    match = re.search(r'^  version "(.*)"$', formula_file.read_text(), re.M)
    if not match:
        die(f"无法读取版本: {formula_file}")
    return match.group(1)


def read_formula_ref(formula_file: Path) -> str:
    match = re.search(r"/archive/([^/]+)\.tar\.gz", formula_file.read_text())
    if not match:
        die(f"无法读取 formula ref: {formula_file}")
    return match.group(1)


def resolve_version_from_ref(explicit: str | None, ref: str) -> str | None:
    if explicit:
        return explicit
    if is_commit_ref(ref):
        return None
    if is_semver_tag(ref):
        return normalize_version(ref)
    return None


def resolve_release(
    repo: str,
    branch: str,
    formula_file: Path,
    explicit_ref: str | None,
    explicit_version: str | None,
    dry_run: bool,
    no_tag_push: bool,
) -> tuple[str, str, str]:
    """返回 (ref, version, commit)。"""
    if explicit_ref:
        version = resolve_version_from_ref(explicit_version, explicit_ref)
        if not version:
            version = read_current_version(formula_file)
        commit = explicit_ref if is_commit_ref(explicit_ref) else get_branch_head(repo, branch)
        if not is_commit_ref(explicit_ref):
            for tag in list_repo_tags(repo):
                if tag["name"] == explicit_ref or normalize_version(tag["name"]) == normalize_version(explicit_ref):
                    commit = tag["commit"]["sha"]
                    break
        return explicit_ref, version, commit

    head = get_branch_head(repo, branch)
    head_tag = best_semver_tag_on_commit(repo, head)
    if head_tag:
        version = normalize_version(head_tag)
        log(f"{repo}: HEAD 已有 tag {head_tag}")
        return head_tag, version, head

    formula_ref = read_formula_ref(formula_file)
    formula_version = read_current_version(formula_file)
    latest_tag_version = latest_semver_tag_version(repo)
    base_versions = [formula_version]
    if latest_tag_version:
        base_versions.append(latest_tag_version)
    if is_semver_tag(formula_ref):
        base_versions.append(normalize_version(formula_ref))

    new_version = increment_patch(max_semver(*base_versions))
    tag_name = f"v{new_version}"

    if formula_ref == head and formula_version == new_version:
        log(f"{repo}: formula 已是最新 commit，等待创建 tag {tag_name}")
    elif formula_ref != head:
        log(f"{repo}: 检测到新 commit {head[:7]}（formula 当前 {formula_ref[:7]}）")
    else:
        log(f"{repo}: HEAD {head[:7]} 无 tag，将递增版本 {formula_version} -> {new_version}")

    if dry_run or no_tag_push:
        log(f"[dry-run] 将创建并推送 tag {tag_name} 到 {repo}")
    else:
        push_tag_ssh(repo, branch, head, tag_name)

    return tag_name, new_version, head


def download_sha256(url: str, *, retries: int = 8, delay_seconds: float = 2.0) -> str:
    last_error: urllib.error.HTTPError | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url) as resp:
                data = resp.read()
            return hashlib.sha256(data).hexdigest()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code != 404 or attempt == retries:
                raise
            log(f"归档暂未就绪，{delay_seconds:.0f}s 后重试 ({attempt}/{retries})")
            time.sleep(delay_seconds)
    if last_error:
        raise last_error
    raise RuntimeError(f"下载失败: {url}")


def update_formula_file(
    formula: str,
    formula_file: Path,
    url: str,
    version: str,
    sha256: str,
    commit: str,
) -> None:
    content = formula_file.read_text()
    content = re.sub(r'^  url ".*"$', f'  url "{url}"', content, count=1, flags=re.M)
    content = re.sub(r'^  version ".*"$', f'  version "{version}"', content, count=1, flags=re.M)
    content = re.sub(r'^  sha256 ".*"$', f'  sha256 "{sha256}"', content, count=1, flags=re.M)

    if formula == "llmwiki":
        short_commit = commit[:7]
        content = re.sub(
            r"-X main\.Commit=[^\s\"]+",
            f"-X main.Commit={short_commit}",
            content,
            count=1,
        )

    formula_file.write_text(content)


def bump_one(
    formula: str,
    explicit_version: str | None,
    explicit_ref: str | None,
    dry_run: bool,
    no_tag_push: bool,
) -> Path:
    if formula not in FORMULAS:
        die(f"未知 formula: {formula}")

    repo, branch = FORMULAS[formula]
    formula_file = FORMULA_DIR / f"{formula}.rb"
    if not formula_file.is_file():
        die(f"找不到 formula 文件: {formula_file}")

    log(f"处理 {formula} ({repo})")

    ref, version, commit = resolve_release(
        repo,
        branch,
        formula_file,
        explicit_ref,
        explicit_version,
        dry_run,
        no_tag_push,
    )

    url = f"https://github.com/{repo}/archive/{ref}.tar.gz"
    log(f"下载 {url}")
    if dry_run or no_tag_push:
        sha256 = "0" * 64
        log("[dry-run] 跳过下载，使用占位 sha256")
    else:
        sha256 = download_sha256(url)

    log(f"{formula}: version={version} ref={ref} commit={commit[:7]} sha256={sha256[:12]}...")

    if dry_run:
        log(f"[dry-run] 将更新 {formula_file}")
        return formula_file

    update_formula_file(formula, formula_file, url, version, sha256, commit)
    log(f"已更新 {formula_file}")
    return formula_file


def git_commit(changed: list[Path], formulas: list[str]) -> None:
    rel_paths = [str(path.relative_to(ROOT)) for path in changed]
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
  scripts/bump-formula.py senv
  scripts/bump-formula.py senv --ref v0.2.0
  scripts/bump-formula.py llmwiki --version 0.2.0 --ref abc1234
  scripts/bump-formula.py --all --no-commit
""",
    )
    parser.add_argument("formulas", nargs="*", help="formula 名称")
    parser.add_argument("--all", action="store_true", help="更新所有 formula")
    parser.add_argument("--version", help="指定 formula 版本")
    parser.add_argument("--ref", help="指定 git tag 或 commit（跳过自动打 tag）")
    parser.add_argument("--no-commit", action="store_true", help="不创建 git commit")
    parser.add_argument("--no-tag-push", action="store_true", help="不向上游推送 tag")
    parser.add_argument("--dry-run", action="store_true", help="预览变更，不写文件、不推送 tag")
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
            bump_one(
                formula,
                args.version,
                args.ref,
                args.dry_run,
                args.no_tag_push,
            )
        )

    if args.dry_run or args.no_commit:
        return

    git_commit(changed, formulas)


if __name__ == "__main__":
    main()
