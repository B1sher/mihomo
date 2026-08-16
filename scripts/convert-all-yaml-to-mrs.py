#!/usr/bin/env python3
"""
Универсальный конвертер YAML → .mrs для Mihomo.

Обрабатывает только доменные списки (domain):
- rules/ads/*.yaml — сливаются в один ads.mrs
- rules/direct.yaml — direct.mrs
- rules/proxy.yaml — proxy.mrs
- Любой другой YAML (кроме programs/) — в .mrs с тем же именем

rules/programs/*.yaml — НЕ конвертируются в .mrs.
Они подключаются в Mihomo напрямую как YAML (format: yaml, behavior: classical).
"""

import sys
import ipaddress
import yaml
import subprocess
from pathlib import Path

RULES_ROOT = Path("rules")
DIST_DIR = Path("dist")
MIHOMO_BIN = "mihomo"

ADS_DIR = RULES_ROOT / "ads"
PROGRAMS_DIR = RULES_ROOT / "programs"

def classify_item(item: str) -> str:
    """Определяет тип строки и возвращает готовое правило."""
    item = item.strip()
    if not item:
        return ""

    # IP или подсеть
    if "/" in item:
        try:
            ipaddress.ip_network(item, strict=False)
            return f"IP-CIDR,{item}"
        except ValueError:
            pass
    else:
        try:
            ipaddress.ip_address(item)
            return f"IP-CIDR,{item}/32"
        except ValueError:
            pass

    # Домен
    return f"DOMAIN-SUFFIX,{item}"

def extract_items_from_yaml(yaml_path: Path) -> list[str]:
    """Извлекает домены из YAML (без payload)."""
    items = []
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    items.append(item)
                elif isinstance(item, dict):
                    items.extend(str(k) for k in item.keys())
        elif isinstance(data, dict):
            items.extend(str(k) for k in data.keys())
    except Exception as e:
        print(f"⚠️ Ошибка чтения {yaml_path}: {e}", file=sys.stderr)

    seen = set()
    unique = []
    for item in items:
        rule = classify_item(item)
        if rule and rule not in seen:
            seen.add(rule)
            unique.append(rule)

    return unique

def convert_to_mrs(items: list[str], output_path: Path):
    """Конвертирует домены в .mrs (domain)."""
    if not items:
        print(f"⚠️ {output_path.name}: нет доменов, создаю пустой .mrs")
        output_path.touch()
        return

    tmp_file = Path(f"/tmp/{output_path.stem}.txt")
    with open(tmp_file, "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"{item}\n")

    # Сначала пробуем classical (поддержка доменов и IP)
    cmd = [MIHOMO_BIN, "convert-ruleset", "classical", "text", str(tmp_file), str(output_path)]
    print(f"🔄 {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️ Classical упал, пробую domain fallback...")
        # Fallback: только домены
        domain_only = [r for r in items if r.startswith("DOMAIN-SUFFIX,")]
        if domain_only:
            tmp_file2 = Path(f"/tmp/{output_path.stem}_domains.txt")
            with open(tmp_file2, "w", encoding="utf-8") as f:
                for item in domain_only:
                    f.write(f"{item}\n")
            cmd2 = [MIHOMO_BIN, "convert-ruleset", "domain", "text", str(tmp_file2), str(output_path)]
            print(f"🔄 Fallback: {' '.join(cmd2)}")
            result2 = subprocess.run(cmd2, capture_output=True, text=True)
            if result2.returncode == 0:
                print(f"✅ {output_path.name}: {len(domain_only)} доменов")
            else:
                print(f"❌ Fallback упал: {result2.stderr}", file=sys.stderr)
                output_path.touch()
        else:
            output_path.touch()
    else:
        print(f"✅ {output_path.name}: {len(items)} правил")

def main():
    if not RULES_ROOT.exists():
        print(f"❌ Директория {RULES_ROOT} не найдена", file=sys.stderr)
        sys.exit(1)

    DIST_DIR.mkdir(exist_ok=True)

    # Ads — слияние
    if ADS_DIR.exists():
        ads_items = []
        for yaml_file in sorted(ADS_DIR.glob("*.yaml")):
            print(f"📄 Ads: {yaml_file.name}")
            ads_items.extend(extract_items_from_yaml(yaml_file))
        convert_to_mrs(ads_items, DIST_DIR / "ads.mrs")

    # Direct
    direct_file = RULES_ROOT / "direct.yaml"
    if direct_file.exists():
        print(f"📄 Direct: {direct_file.name}")
        convert_to_mrs(extract_items_from_yaml(direct_file), DIST_DIR / "direct.mrs")

    # Proxy
    proxy_file = RULES_ROOT / "proxy.yaml"
    if proxy_file.exists():
        print(f"📄 Proxy: {proxy_file.name}")
        convert_to_mrs(extract_items_from_yaml(proxy_file), DIST_DIR / "proxy.mrs")

    # Другие YAML (кроме programs/ — они идут напрямую)
    for yaml_file in sorted(RULES_ROOT.rglob("*.yaml")):
        if ADS_DIR in yaml_file.parents:
            continue
        if PROGRAMS_DIR in yaml_file.parents:
            continue
        if yaml_file.name in ("direct.yaml", "proxy.yaml"):
            continue

        print(f"📄 Прочее: {yaml_file.relative_to(RULES_ROOT)}")
        output_name = yaml_file.stem + ".mrs"
        convert_to_mrs(extract_items_from_yaml(yaml_file), DIST_DIR / output_name)

    print("\n✅ Все конвертации завершены")
    print(f"📦 Результаты в {DIST_DIR}/")
    print(f"ℹ️ Programs (rules/programs/) не конвертируются — используются напрямую как YAML")

if __name__ == "__main__":
    main()
