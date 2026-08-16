#!/usr/bin/env python3
"""
Конвертирует rules/programs/programs_direct.yaml в текстовый формат
для mihomo convert-ruleset (classical).

Читает: rules/programs/programs_direct.yaml (с payload:)
Пишет: /tmp/combined-programs-direct.txt в формате PROCESS-NAME,... или PROCESS-NAME-REGEX,...
"""

import sys
import yaml
from pathlib import Path

RULES_FILE = Path("rules/programs/programs_direct.yaml")
OUTPUT_FILE = Path("/tmp/combined-programs-direct.txt")

def main():
    if not RULES_FILE.exists():
        print(f"❌ Файл {RULES_FILE} не найден", file=sys.stderr)
        sys.exit(1)

    with open(RULES_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    rules = []
    if isinstance(data, dict) and "payload" in data:
        payload = data["payload"]
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, str):
                    rules.append(item)
                elif isinstance(item, dict):
                    rules.extend(str(k) for k in item.keys())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for rule in rules:
            f.write(f"{rule}\n")

    print(f"✅ Правил: {len(rules)}")
    print(f"📦 Файл для конвертации: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
