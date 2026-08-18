#!/usr/bin/env python3
"""
Обновляет README.md — вставляет автоматически сгенерированные
raw-ссылки на .mrs файлы (ветка mrs) и .yaml файлы (ветка main, programs).

Ищет маркеры в README.md:
<!-- MRS_LINKS_START -->
... ссылки на .mrs ...
<!-- MRS_LINKS_END -->

<!-- YAML_LINKS_START -->
... ссылки на .yaml ...
<!-- YAML_LINKS_END -->
"""

import re
from pathlib import Path

REPO = "B1sher/mihomo"
MRS_BRANCH = "mrs"
MAIN_BRANCH = "main"

MRS_DIR = Path("mrs")
PROGRAMS_DIR = Path("rules/programs")

README_PATH = Path("README.md")

MRS_LINKS_START = "<!-- MRS_LINKS_START -->"
MRS_LINKS_END = "<!-- MRS_LINKS_END -->"
YAML_LINKS_START = "<!-- YAML_LINKS_START -->"
YAML_LINKS_END = "<!-- YAML_LINKS_END -->"

def generate_mrs_links() -> str:
    """Генерирует блок raw-ссылок на .mrs файлы."""
    links = []
    if MRS_DIR.exists():
        for mrs_file in sorted(MRS_DIR.glob("*.mrs")):
            name = mrs_file.name
            size = mrs_file.stat().st_size
            size_h = f"{size} B" if size < 1024 else f"{size / 1024:.1f} KB"
            links.append(f"- [{name}](https://raw.githubusercontent.com/{REPO}/{MRS_BRANCH}/{name}) — {size_h}")
    return "\n".join(links)

def generate_yaml_links() -> str:
    """Генерирует блок raw-ссылок на .yaml файлы из programs/."""
    links = []
    if PROGRAMS_DIR.exists():
        for yaml_file in sorted(PROGRAMS_DIR.glob("*.yaml")):
            name = yaml_file.name
            rel_path = yaml_file.as_posix()
            links.append(f"- [{name}](https://raw.githubusercontent.com/{REPO}/{MAIN_BRANCH}/{rel_path})")
    return "\n".join(links)

def update_readme():
    """Обновляет README.md — заменяет блоки между маркерами."""
    if not README_PATH.exists():
        print(f"⚠️ {README_PATH} не найден, создаю новый")
        README_PATH.write_text("", encoding="utf-8")

    content = README_PATH.read_text(encoding="utf-8")

    # Обновляем .mrs ссылки
    mrs_links = generate_mrs_links()
    mrs_block = f"{MRS_LINKS_START}\n{mrs_links}\n{MRS_LINKS_END}"

    if MRS_LINKS_START in content and MRS_LINKS_END in content:
        pattern = re.compile(
            f"{re.escape(MRS_LINKS_START)}.*?{re.escape(MRS_LINKS_END)}",
            re.DOTALL,
        )
        content = pattern.sub(mrs_block, content)
    else:
        content += f"\n{mrs_block}\n"

    # Обновляем .yaml ссылки
    yaml_links = generate_yaml_links()
    yaml_block = f"{YAML_LINKS_START}\n{yaml_links}\n{YAML_LINKS_END}"

    if YAML_LINKS_START in content and YAML_LINKS_END in content:
        pattern = re.compile(
            f"{re.escape(YAML_LINKS_START)}.*?{re.escape(YAML_LINKS_END)}",
            re.DOTALL,
        )
        content = pattern.sub(yaml_block, content)
    else:
        content += f"\n{yaml_block}\n"

    README_PATH.write_text(content, encoding="utf-8")
    print("✅ README.md обновлён")

if __name__ == "__main__":
    update_readme()
