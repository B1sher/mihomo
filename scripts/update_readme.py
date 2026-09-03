#!/usr/bin/env python3
import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = "B1sher/mihomo"
LISTS_BRANCH = "lists"
MAIN_BRANCH = "main"

APPS_DIR = Path("rules/apps")
README_PATH = Path("README.md")

LINKS_START = "<!-- LINKS_START -->"
LINKS_END = "<!-- LINKS_END -->"

# Списки в ветке lists
LISTS_FILES = [
    ("ads_pc.mrs", "mrs"),
    ("ads_phone.mrs", "mrs"),
    ("direct.mrs", "mrs"),
    ("proxy.mrs", "mrs"),
    ("hosts_pc.list", "list"),
    ("hosts_android.list", "list"),
    ("hosts_universal.list", "list"),
]

LOCAL_TZ = timezone(timedelta(hours=3))


def get_file_commit_time(name):
    """Возвращает (время, дату) последнего коммита файла в ветке lists."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ai", f"origin/{LISTS_BRANCH}", "--", name],
            capture_output=True, text=True, check=True,
        )
        commit_time_str = result.stdout.strip()
        if not commit_time_str:
            return None, None

        commit_time = datetime.fromisoformat(commit_time_str)
        commit_time = commit_time.astimezone(LOCAL_TZ)
        return commit_time.strftime("%H:%M"), commit_time.strftime("%d.%m.%y")
    except Exception:
        return None, None


def get_apps_file_time(yaml_file):
    """Возвращает (время, дату) последнего коммита файла в main."""
    try:
        rel_path = yaml_file.as_posix()
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ai", "origin/main", "--", rel_path],
            capture_output=True, text=True, check=True,
        )
        commit_time_str = result.stdout.strip()
        if not commit_time_str:
            return None, None

        commit_time = datetime.fromisoformat(commit_time_str)
        commit_time = commit_time.astimezone(LOCAL_TZ)
        return commit_time.strftime("%H:%M"), commit_time.strftime("%d.%m.%y")
    except Exception:
        return None, None


def generate_unified_table():
    rows = []
    rows.append("| Файл | Формат | Время (UTC+3) | Дата |")
    rows.append("|------|--------|---------------|------|")

    for name, fmt in LISTS_FILES:
        url = f"https://raw.githubusercontent.com/{REPO}/{LISTS_BRANCH}/{name}"
        display_name = Path(name).stem
        time_part, date_part = get_file_commit_time(name)
        if time_part is None:
            time_part, date_part = "—", "—"
        rows.append(f"| [{display_name}]({url}) | `{fmt}` | {time_part} | {date_part} |")

    if APPS_DIR.exists():
        for yaml_file in sorted(APPS_DIR.glob("*.yaml")):
            rel_path = yaml_file.as_posix()
            url = f"https://raw.githubusercontent.com/{REPO}/{MAIN_BRANCH}/{rel_path}"
            display_name = yaml_file.stem
            time_part, date_part = get_apps_file_time(yaml_file)
            if time_part is None:
                time_part, date_part = "—", "—"
            rows.append(f"| [{display_name}]({url}) | `yaml` | {time_part} | {date_part} |")

    return "\n".join(rows)


def update_readme():
    if not README_PATH.exists():
        print(f"Error: {README_PATH} not found")
        return

    content = README_PATH.read_text(encoding="utf-8")

    table = generate_unified_table()
    block = f"{LINKS_START}\n\n{table}\n\n{LINKS_END}"

    if LINKS_START in content and LINKS_END in content:
        pattern = re.compile(
            f"{re.escape(LINKS_START)}.*?{re.escape(LINKS_END)}",
            re.DOTALL,
        )
        content = pattern.sub(block, content)
    else:
        content += f"\n{block}\n"

    README_PATH.write_text(content, encoding="utf-8")
    print("OK: README updated")


if __name__ == "__main__":
    update_readme()