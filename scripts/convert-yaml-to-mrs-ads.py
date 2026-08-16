#!/usr/bin/env python3
"""
Конвертирует YAML-файлы с рекламными доменами в текстовый формат
для mihomo convert-ruleset (domain).

Читает: rules/ads/*.yaml
Пишет: /tmp/combined-ads.txt в формате DOMAIN-SUFFIX,domain.com
"""

import sys
import yaml
from pathlib import Path

RULES_DIR = Path("rules/ads")
OUTPUT_FILE = Path("/tmp/combined-ads.txt")

def extract_domains_from_yaml(yaml_path: Path) -> list[str]:
    """Извлекает домены из YAML-файла, игнорируя комментарии."""
    domains = []
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    domains.append(item)
                elif isinstance(item, dict):
                    domains.extend(str(k) for k in item.keys())
        elif isinstance(data, dict):
            domains.extend(str(k) for k in data.keys())
    except Exception as e:
        print(f"⚠️ Ошибка чтения {yaml_path}: {e}", file=sys.stderr)

    return domains

def main():
    if not RULES_DIR.exists():
        print(f"❌ Директория {RULES_DIR} не найдена", file=sys.stderr)
        sys.exit(1)

    all_domains = []
    yaml_files = sorted(RULES_DIR.glob("*.yaml"))

    if not yaml_files:
        print(f"❌ Нет .yaml файлов в {RULES_DIR}", file=sys.stderr)
        sys.exit(1)

    for yaml_file in yaml_files:
        print(f"📄 Обрабатываю {yaml_file.name}...")
        domains = extract_domains_from_yaml(yaml_file)
        print(f"   Найдено доменов: {len(domains)}")
        all_domains.extend(domains)

    seen = set()
    unique_domains = []
    for d in all_domains:
        if d not in seen:
            seen.add(d)
            unique_domains.append(d)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for domain in unique_domains:
            f.write(f"DOMAIN-SUFFIX,{domain}\n")

    print(f"\n✅ Итого уникальных доменов: {len(unique_domains)}")
    print(f"📦 Файл для конвертации: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
