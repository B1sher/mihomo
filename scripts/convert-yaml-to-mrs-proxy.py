#!/usr/bin/env python3
"""
Конвертирует rules/proxy.yaml в текстовый формат для mihomo convert-ruleset (domain).

Читает: rules/proxy.yaml
Пишет: /tmp/combined-proxy.txt в формате DOMAIN-SUFFIX,domain.com
"""

import sys
import yaml
from pathlib import Path

RULES_FILE = Path("rules/proxy.yaml")
OUTPUT_FILE = Path("/tmp/combined-proxy.txt")

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

    seen = set()
    unique_domains = []
    for d in domains:
        if d not in seen:
            seen.add(d)
            unique_domains.append(d)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for domain in unique_domains:
            f.write(f"DOMAIN-SUFFIX,{domain}\n")

    print(f"✅ Уникальных доменов: {len(unique_domains)}")
    print(f"📦 Файл для конвертации: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
