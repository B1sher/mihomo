#!/usr/bin/env python3
"""
Обновляет README.md — вставляет автоматически сгенерированные
raw-ссылки на .mrs файлы (из ветки mrs) и .yaml файлы (из programs/).

Дизайн единый: таблица с кликабельным именем файла и временем обновления.
Время: ЧЧ:ММ ДД.ММ.ГГ (одна строка).
"""

import re
from datetime import datetime, timezone
from pathlib import Path

REPO = "B1sher/mihomo"
MRS_BRANCH = "mrs"
MAIN_BRANCH = "main"

PROGRAMS_DIR = Path("rules/programs")
README_PATH = Path("README.md")

MRS_LINKS_START = "<!-- MRS_LINKS_START -->"
MRS_LINKS_END = "<!-- MRS_LINKS_END -->"
YAML_LINKS_START = "<!-- YAML_LINKS_START -->"
YAML_LINKS_END = "<!-- YAML_LINKS_END -->"

MRS_FILES = [
    "ads_pc.mrs",
    "ads_phone.mrs",
    "direct.mrs",
    "proxy.mrs",
]

def get_current_time():
    """Возвращает время в формате ЧЧ:ММ ДД.ММ.ГГ (UTC)."""
    now = datetime.now(timezone.utc)
    return now.strftime("%H:%M %d.%m.%y")

def generate_mrs_table():
    time_str = get_current_time()
    rows = []
    rows.append("| Файл | Обновлён |")
    rows.append("|------|----------|")

    for name in MRS_FILES:
        url = f"https://raw.githubusercontent.com/{REPO}/{MRS_BRANCH}/{name}"
        rows.append(f"| [{name}]({url}) | {time_str} |")

    return "\n".join(rows)

def generate_yaml_table():
    time_str = get_current_time()
    rows = []
    rows.append("| Файл | Обновлён |")
    rows.append("|------|----------|")

    if PROGRAMS_DIR.exists():
        for yaml_file in sorted(PROGRAMS_DIR.glob("*.yaml")):
            name = yaml_file.name
            rel_path = yaml_file.as_posix()
            url = f"https://raw.githubusercontent.com/{REPO}/{MAIN_BRANCH}/{rel_path}"
            rows.append(f"| [{name}]({url}) | {time_str} |")

    return "\n".join(rows)

def update_readme():
    if not README_PATH.exists():
        print(f"Ошибка: {README_PATH} не найден")
        return

    content = README_PATH.read_text(encoding="utf-8")

    # Обновляем .mrs таблицу
    mrs_table = generate_mrs_table()
    mrs_block = f"{MRS_LINKS_START}\n\n{mrs_table}\n\n{MRS_LINKS_END}"

    if MRS_LINKS_START in content and MRS_LINKS_END in content:
        pattern = re.compile(
            f"{re.escape(MRS_LINKS_START)}.*?{re.escape(MRS_LINKS_END)}",
            re.DOTALL,
        )
        content = pattern.sub(mrs_block, content)
    else:
        content += f"\n{mrs_block}\n"

    # Обновляем .yaml таблицу
    yaml_table = generate_yaml_table()
    yaml_block = f"{YAML_LINKS_START}\n\n{yaml_table}\n\n{YAML_LINKS_END}"

    if YAML_LINKS_START in content and YAML_LINKS_END in content:
        pattern = re.compile(
            f"{re.escape(YAML_LINKS_START)}.*?{re.escape(YAML_LINKS_END)}",
            re.DOTALL,
        )
        content = pattern.sub(yaml_block, content)
    else:
        content += f"\n{yaml_block}\n"

    README_PATH.write_text(content, encoding="utf-8")
    print("OK: README.md обновлён")

if __name__ == "__main__":
    update_readme()
