#!/usr/bin/env python3
"""
Конвертирует rules/programs/programs_direct.yaml в текстовый формат
для mihomo convert-ruleset (classical).

Читает: rules/programs/programs_direct.yaml (с payload:)
Пишет: /tmp/combined-programs-direct.txt в формате PROCESS-NAME,... или PROCESS-NAME-REGEX,...
Если правил нет — создаёт пустой файл и выходит с кодом 0.
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

    # Убираем пустые строки и дубликаты
    seen = set()
    unique_rules = []
    for r in rules:
        r = r.strip()
        if r and r not in seen:
            seen.add(r)
            unique_rules.append(r)

    # Если правил нет — создаём пустой файл
    if not unique_rules:
        print("⚠️ Правил нет — создаю пустой файл")
        OUTPUT_FILE.write_text("", encoding="utf-8")
        print(f"📦 Файл для конвертации: {OUTPUT_FILE}")
        sys.exit(0)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for rule in unique_rules:
            f.write(f"{rule}\n")

    print(f"✅ Правил: {len(unique_rules)}")
    print(f"📦 Файл для конвертации: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
