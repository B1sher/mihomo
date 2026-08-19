#!/usr/bin/env python3
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = "B1sher/mihomo"
MRS_BRANCH = "mrs"
MAIN_BRANCH = "main"

APPS_DIR = Path("rules/apps")
README_PATH = Path("README.md")

LINKS_START = "<!-- LINKS_START -->"
LINKS_END = "<!-- LINKS_END -->"

MRS_FILES = [
    "ads_pc.mrs",
    "ads_phone.mrs",
    "direct.mrs",
    "proxy.mrs",
]

# Часовой пояс UTC+3 (Москва)
LOCAL_TZ = timezone(timedelta(hours=3))

def get_current_time():
    now = datetime.now(LOCAL_TZ)
    return now.strftime("%H:%M %d.%m.%y")

def generate_unified_table():
    time_str = get_current_time()
    rows = []
    rows.append("| Файл | Формат | Обновлён (UTC+3) |")
    rows.append("|------|--------|------------------|")

    for name in MRS_FILES:
        url = f"https://raw.githubusercontent.com/{REPO}/{MRS_BRANCH}/{name}"
        display_name = Path(name).stem
        rows.append(f"| [{display_name}]({url}) | `mrs` | {time_str} |")

    if APPS_DIR.exists():
        for yaml_file in sorted(APPS_DIR.glob("*.yaml")):
            name = yaml_file.name
            rel_path = yaml_file.as_posix()
            url = f"https://raw.githubusercontent.com/{REPO}/{MAIN_BRANCH}/{rel_path}"
            display_name = yaml_file.stem
            rows.append(f"| [{display_name}]({url}) | `yaml` | {time_str} |")

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
