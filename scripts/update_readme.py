#!/usr/bin/env python3
"""
Обновляет README.md — вставляет автоматически сгенерированные
raw-ссылки на .mrs файлы (из ветки mrs) и .yaml файлы (из programs/).

Единая таблица: Файл | Тип | Копировать | Обновлён
"""

import re
from datetime import datetime, timezone
from pathlib import Path

REPO = "B1sher/mihomo"
MRS_BRANCH = "mrs"
MAIN_BRANCH = "main"

PROGRAMS_DIR = Path("rules/programs")
README_PATH = Path("README.md")

LINKS_START = "<!-- LINKS_START -->"
LINKS_END = "<!-- LINKS_END -->"

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

def generate_unified_table():
    """Генерирует единую таблицу с .mrs и .yaml файлами."""
    time_str = get_current_time()
    rows = []
    rows.append("| Файл | Тип | Копировать | Обновлён |")
    rows.append("|------|-----|------------|----------|")

    # .mrs файлы
    for name in MRS_FILES:
        url = f"https://raw.githubusercontent.com/{REPO}/{MRS_BRANCH}/{name}"
        rows.append(f"| [{name}]({url}) | `mrs` | `{url}` | {time_str} |")

    # .yaml файлы из programs/
    if PROGRAMS_DIR.exists():
        for yaml_file in sorted(PROGRAMS_DIR.glob("*.yaml")):
            name = yaml_file.name
            rel_path = yaml_file.as_posix()
            url = f"https://raw.githubusercontent.com/{REPO}/{MAIN_BRANCH}/{rel_path}"
            rows.append(f"| [{name}]({url}) | `yaml` | `{url}` | {time_str} |")

    return "\n".join(rows)

def update_readme():
    if not README_PATH.exists():
        print(f"Ошибка: {README_PATH} не найден")
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
    print("OK: README.md обновлён")

if __name__ == "__main__":
    update_readme()
