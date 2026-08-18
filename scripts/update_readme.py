#!/usr/bin/env python3
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
    now = datetime.now(timezone.utc)
    return now.strftime("%H:%M %d.%m.%y")

def generate_unified_table():
    time_str = get_current_time()
    rows = []
    rows.append("| Файл | Формат | Обновлён |")
    rows.append("|------|--------|----------|")

    for name in MRS_FILES:
        url = f"https://raw.githubusercontent.com/{REPO}/{MRS_BRANCH}/{name}"
        display_name = Path(name).stem
        rows.append(f"| [{display_name}]({url}) | `mrs` | {time_str} |")

    if PROGRAMS_DIR.exists():
        for yaml_file in sorted(PROGRAMS_DIR.glob("*.yaml")):
            name = y
