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

# Категории файлов в ветке lists
ADS_FILES = [
    ("ads_pc.mrs", "mrs"),
    ("ads_phone.mrs", "mrs"),
]

HOSTS_FILES = [
    ("hosts_pc.list", "list"),
    ("hosts_phone.list", "list"),
    ("hosts_universal.list", "list"),
]

CUSTOM_ROUTES_FILES = [
    ("direct.mrs", "mrs"),
    ("proxy.mrs", "mrs"),
]

LOCAL_TZ = timezone(timedelta(hours=3))


def get_file_commit_time(name, branch):
    """Возвращает (время, дату) последнего коммита файла в ветке."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ai", f"origin/{branch}", "--", name],
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


def add_table_row(rows, name, fmt, branch):
    url = f"https://raw.githubusercontent.com/{REPO}/{branch}/{name}"
    display_name = Path(name).stem
    time_part, date_part = get_file_commit_time(name, branch)
    if time_part is None:
        time_part, date_part = "—", "—"
    rows.append(f"| [{display_name}]({url}) | `{fmt}` | {time_part} | {date_part} |")


def generate_unified_table():
    rows = []

    # Заголовок таблицы
    rows.append("| Файл | Формат | Время (UTC+3) | Дата |")
    rows.append("|------|--------|---------------|------|")

    # 1. Реклама и телеметрия
    rows.append("| **1. Реклама и телеметрия** | | | |")
    for name, fmt in ADS_FILES:
        add_table_row(rows, name, fmt, LISTS_BRANCH)

    # 2. Hosts
    rows.append("| **2. Hosts** | | | |")
    for name, fmt in HOSTS_FILES:
        add_table_row(rows, name, fmt, LISTS_BRANCH)

    # 3. Кастомные маршруты
    rows.append("| **3. Кастомные маршруты** | | | |")
    for name, fmt in CUSTOM_ROUTES_FILES:
        add_table_row(rows, name, fmt, LISTS_BRANCH)

    # 4. Приложения
    if APPS_DIR.exists():
        rows.append("| **4. Приложения** | | | |")
        for yaml_file in sorted(APPS_DIR.glob("*.yaml")):
            rel_path = yaml_file.as_posix()
            display_name = yaml_file.stem
            url = f"https://raw.githubusercontent.com/{REPO}/{MAIN_BRANCH}/{rel_path}"
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