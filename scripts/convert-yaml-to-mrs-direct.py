#!/usr/bin/env python3
"""
Конвертирует rules/direct.yaml в текстовый формат для mihomo convert-ruleset (domain).

Читает: rules/direct.yaml
Пишет: /tmp/combined-direct.txt в формате DOMAIN-SUFFIX,domain.com
Если доменов нет — создаёт пустой файл и выходит с кодом 0.
"""

import sys
import yaml
from pathlib import Path

RULES_FILE = Path("rules/direct.yaml")
OUTPUT_FILE = Path("/tmp/combined-direct.txt")

def main():
    if not RULES_FILE.exists():
        print(f"❌ Файл {RULES_FILE} не найден", file=sys.stderr)
        sys.exit(1)

    with open(RULES_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    domains = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                domains.append(item)
            elif isinstance(item, dict):
                domains.extend(str(k) for k in item.keys())
    elif isinstance(data, dict):
        domains.extend(str(k) for k in data.keys())

    # Убираем пустые строки и дубликаты
    seen = set()
    unique_domains = []
    for d in domains:
        d = d.strip()
        if d and d not in seen:
            seen.add(d)
            unique_domains.append(d)

    # Если доменов нет — создаём пустой файл
    if not unique_domains:
        print("⚠️ Доменов нет — создаю пустой файл")
        OUTPUT_FILE.write_text("", encoding="utf-8")
        print(f"📦 Файл для конвертации: {OUTPUT_FILE}")
        sys.exit(0)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for domain in unique_domains:
            f.write(f"DOMAIN-SUFFIX,{domain}\n")

    print(f"✅ Уникальных доменов: {len(unique_domains)}")
    print(f"📦 Файл для конвертации: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
