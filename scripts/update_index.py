#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""liuyun847/liuyun847 仓库索引生成器（Python 3.12，仅标准库）。

流程：拉取账号下的公开仓库列表 → 按规则分组 → 渲染 Markdown →
替换 README.md 中 ``<!-- AUTO:START -->`` 与 ``<!-- AUTO:END -->`` 之间的内容。
标记之外的手写部分一律不动；生成结果与文件现有内容完全一致时不写文件。

分组优先级（由高到低，与 repos.toml 头部注释保持一致）：
  1. repos.toml 的 [repos] 表显式指定的组（最权威，用于纠正前缀规则的误判）
  2. 仓库 topics 命中某个组的 id（例如给仓库打 dsh-experiment topic）
  3. 仓库名以 dsh- 开头 → DSH 插件组
  4. fork: true → Fork 组
  5. 都没命中 → 未分类组（该组没有仓库时不输出这一节）

用法：
  python scripts/update_index.py                      # 调 GitHub API，写 README.md
  python scripts/update_index.py --dry-run            # 只打印生成结果，不写文件
  python scripts/update_index.py --repos-json f.json  # 离线：从本地 JSON 读仓库列表

环境变量：GITHUB_TOKEN 存在时带 Authorization 头（匿名也能用，限额 60 次/小时）。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

USER = "liuyun847"  # 被索引的账号
API_URL = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=full_name"

REPO_ROOT = Path(__file__).resolve().parents[1]  # 仓库根目录（脚本在 scripts/ 下）
CONFIG_PATH = REPO_ROOT / "repos.toml"
README_PATH = REPO_ROOT / "README.md"

AUTO_START = "<!-- AUTO:START -->"
AUTO_END = "<!-- AUTO:END -->"

DSH_PREFIX = "dsh-"  # 命中该前缀的仓库默认进 DSH 插件组
DSH_PREFIX_GROUP = "dsh-plugin"
FALLBACK_GROUP = "uncategorized"  # 兜底组，强制排在最后
TZ_NAME = "Asia/Shanghai"


def shanghai_tz() -> timezone | ZoneInfo:
    """返回 Asia/Shanghai 时区。

    标准库 zoneinfo 依赖系统 tzdata：Linux/macOS 自带，Windows 没装 tzdata 包时
    会抛 ZoneInfoNotFoundError，此时退化成固定 +08:00（中国不实行夏令时，等价）。
    """
    try:
        return ZoneInfo(TZ_NAME)
    except Exception:  # noqa: BLE001 - 任何取不到 tzdata 的情况都走退化分支
        print(f"[warn] 取不到 {TZ_NAME} 时区数据，退化为固定 +08:00", file=sys.stderr)
        return timezone(timedelta(hours=8), TZ_NAME)


# ---------------------------------------------------------------------------
# 取数据
# ---------------------------------------------------------------------------


def api_headers() -> dict[str, str]:
    """构造 API 请求头；有 GITHUB_TOKEN 就带上（匿名 60 次/小时也够用）。"""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": f"{USER}-index-updater",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def next_page_url(link_header: str | None) -> str | None:
    """从 Link 响应头里取出 rel="next" 的 URL，没有下一页就返回 None。"""
    if not link_header:
        return None
    for part in link_header.split(","):
        url, _, params = part.partition(";")
        if 'rel="next"' in params:
            return url.strip().strip("<>")
    return None


def fetch_repos(headers: dict[str, str]) -> list[dict]:
    """按 Link 头翻页，取全量仓库列表。"""
    repos: list[dict] = []
    url: str | None = API_URL
    page = 0
    while url:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            batch = json.load(response)
            repos.extend(batch)
            url = next_page_url(response.headers.get("Link"))
        page += 1
        print(f"[api] 第 {page} 页：{len(batch)} 个仓库", file=sys.stderr)
    return repos


def fill_fork_parent(repos: list[dict], headers: dict[str, str]) -> None:
    """给 fork 仓库补齐 parent 字段。

    列表接口不返回 parent（只有单仓库详情接口才有），而 README 的 Fork 组要显示
    上游链接，所以对 fork 仓库额外查一次详情；失败只告警，不影响其余渲染。
    """
    for repo in repos:
        if not repo.get("fork") or repo.get("parent") or not repo.get("url"):
            continue
        try:
            request = urllib.request.Request(repo["url"], headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                detail = json.load(response)
            repo["parent"] = detail.get("parent")
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(
                f"[warn] 取 {repo.get('full_name')} 的 parent 失败：{exc}",
                file=sys.stderr,
            )


# ---------------------------------------------------------------------------
# 读配置
# ---------------------------------------------------------------------------


def load_config(path: Path) -> tuple[list[dict], dict[str, str], set[str]]:
    """读 repos.toml，返回（组列表、显式映射、排除名单）。

    组列表已按显示顺序排好：groups 数组顺序 + uncategorized 强制最后。
    """
    with path.open("rb") as fp:
        config = tomllib.load(fp)

    groups: list[dict] = list(config.get("groups") or [])
    if not groups:
        raise SystemExit(f"{path} 里没有 [[groups]]，无法生成")

    ids = [group.get("id") for group in groups]
    if any(not isinstance(gid, str) or not gid for gid in ids):
        raise SystemExit(f"{path} 里有 [[groups]] 缺少 id")
    if len(set(ids)) != len(ids):
        raise SystemExit(f"{path} 里有重复的组 id：{ids}")
    if FALLBACK_GROUP not in ids:
        raise SystemExit(f"{path} 里缺少兜底组 id = {FALLBACK_GROUP!r}")
    if DSH_PREFIX_GROUP not in ids:
        raise SystemExit(
            f"{path} 里缺少 dsh- 前缀规则的落点组 id = {DSH_PREFIX_GROUP!r}"
        )

    # uncategorized 强制排在最后
    groups = [g for g in groups if g["id"] != FALLBACK_GROUP]
    groups.append(next(g for g in config["groups"] if g["id"] == FALLBACK_GROUP))

    repos_map: dict[str, str] = dict(config.get("repos") or {})
    for name, gid in repos_map.items():
        if gid not in ids:
            raise SystemExit(f"{path} 的 [repos] 里 {name} 指向不存在的组 {gid!r}")

    exclude = {str(item) for item in (config.get("exclude") or [])}
    return groups, repos_map, exclude


# ---------------------------------------------------------------------------
# 分组与渲染
# ---------------------------------------------------------------------------


def group_of(repo: dict, repos_map: dict[str, str], group_ids: list[str]) -> str:
    """按优先级判定仓库属于哪个组。"""
    name = repo.get("name") or ""

    # 1) 显式映射最权威
    if name in repos_map:
        return repos_map[name]

    # 2) topics 命中组 id；多个命中时按 groups 顺序取第一个，保证结果稳定
    topics = set(repo.get("topics") or [])
    for gid in group_ids:
        if gid in topics:
            return gid

    # 3) dsh- 前缀
    if name.startswith(DSH_PREFIX):
        return DSH_PREFIX_GROUP

    # 4) fork
    if repo.get("fork"):
        return "fork"

    # 5) 兜底
    return FALLBACK_GROUP


def describe(repo: dict) -> str:
    """生成「说明」列：仓库 description（为空写 —），fork 追加上游链接。"""
    desc = (repo.get("description") or "").strip()
    parent = repo.get("parent") or {}
    if repo.get("fork") and parent.get("full_name"):
        full_name = parent["full_name"]
        url = parent.get("html_url") or f"https://github.com/{full_name}"
        upstream = f"上游 [{full_name}]({url}) 的 fork"
        return f"{desc}；{upstream}" if desc else upstream
    return desc or "—"


def render_block(groups: list[dict], buckets: dict[str, list[dict]], today: str) -> str:
    """渲染自动区块：首行最后更新时间 + 每组标题/说明/两列表格。"""
    lines = [f"最后更新：{today}", ""]
    for group in groups:
        items = buckets.get(group["id"]) or []
        if not items:
            continue  # 空组不输出（未分类组为空时整节消失）
        lines.append(f"## {group['title']}")
        lines.append("")
        intro = (group.get("intro") or "").strip()
        if intro:
            lines.append(intro)
            lines.append("")
        lines.append("| 仓库 | 说明 |")
        lines.append("|---|---|")
        for repo in items:
            lines.append(f"| [{repo['name']}]({repo['html_url']}) | {describe(repo)} |")
        lines.append("")
    # 结尾留一个换行：写入后 <!-- AUTO:END --> 前面会有一行空行，源码更清爽
    return "\n".join(lines).rstrip("\n") + "\n"


def splice(readme: str, block: str) -> str:
    """把 block 放进 AUTO 标记之间，标记之外的内容原样保留。"""
    start = readme.find(AUTO_START)
    end = readme.find(AUTO_END)
    if start == -1 or end == -1:
        raise SystemExit(f"README.md 里找不到 {AUTO_START} / {AUTO_END} 标记")
    if end < start:
        raise SystemExit("README.md 里 AUTO 标记的顺序反了")
    return f"{readme[: start + len(AUTO_START)]}\n{block}\n{readme[end:]}"


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 README.md 里的仓库索引自动区块")
    parser.add_argument(
        "--repos-json",
        type=Path,
        help="从本地 JSON 文件读仓库列表，替代调 API（离线测试用）",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="只打印生成结果，不写文件"
    )
    args = parser.parse_args(argv)

    groups, repos_map, exclude = load_config(CONFIG_PATH)
    group_ids = [group["id"] for group in groups]

    if args.repos_json:
        repos = json.loads(args.repos_json.read_text(encoding="utf-8"))
        print(
            f"[info] 离线模式：{args.repos_json} 里有 {len(repos)} 个仓库",
            file=sys.stderr,
        )
    else:
        headers = api_headers()
        mode = "带 token" if os.environ.get("GITHUB_TOKEN") else "匿名"
        repos = fetch_repos(headers)
        fill_fork_parent(repos, headers)
        print(f"[info] API 模式（{mode}）：共 {len(repos)} 个仓库", file=sys.stderr)

    buckets: dict[str, list[dict]] = {gid: [] for gid in group_ids}
    for repo in repos:
        name = repo.get("name") or ""
        full_name = repo.get("full_name") or name
        if name in exclude or full_name in exclude:
            print(f"[skip] 已排除 {full_name}", file=sys.stderr)
            continue
        buckets[group_of(repo, repos_map, group_ids)].append(repo)

    for gid in group_ids:  # 组内按仓库名字典序，稳定输出、减少无谓 diff
        buckets[gid].sort(key=lambda repo: repo["name"])
        names = "、".join(repo["name"] for repo in buckets[gid]) or "-"
        print(f"[group] {gid}: {names}", file=sys.stderr)

    today = datetime.now(shanghai_tz()).strftime("%Y-%m-%d")
    block = render_block(groups, buckets, today)

    old_text = README_PATH.read_text(encoding="utf-8")
    new_text = splice(old_text, block)

    if args.dry_run:
        # dry-run 只打印不落盘：不管有没有变化都把生成结果完整打出来，方便肉眼检查
        if new_text == old_text:
            print("无变化")
        print(new_text)
        print("[info] --dry-run：未写入文件", file=sys.stderr)
        return 0

    if new_text == old_text:
        print("无变化")
        return 0

    README_PATH.write_text(new_text, encoding="utf-8", newline="\n")
    total = sum(len(items) for items in buckets.values())
    used = sum(1 for gid in group_ids if buckets[gid])
    print(f"已更新 {README_PATH.name}：{total} 个仓库 / {used} 个分组")
    return 0


if __name__ == "__main__":
    sys.exit(main())
