#!/usr/bin/env python3
"""
Универсальный конвертер YAML → .mrs для Mihomo.

Обрабатывает только доменные списки (domain):
- rules/ads/pc.yaml + crossplatform.yaml → mrs/ads_pc.mrs
- rules/ads/android.yaml + crossplatform.yaml → mrs/ads_mobile.mrs
- rules/direct.yaml → mrs/direct.mrs
- rules/proxy.yaml → mrs/proxy.mrs
- Любой другой YAML (кроме programs/) → mrs/<имя>.mrs

rules/programs/*.yaml — НЕ конвертируются в .mrs.
Они подключаются в Mihomo напрямую как YAML (format: yaml, behavior: classical).
"""

import sys
import ipaddress
import yaml
import subprocess
from pathlib import Path

RULES_ROOT = Path("rules")
MRS_DIR = Path("mrs")
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

def merge_unique(*item_lists: list[str]) -> list[str]:
    """Сливает несколько списков, убирая дубликаты."""
    seen = set()
    unique = []
    for items in item_lists:
        for item in items:
            if item and item not in seen:
                seen.add(item)
                unique.append(item)
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

    MRS_DIR.mkdir(exist_ok=True)

    # Ads — разделяем на PC и Mobile
    if ADS_DIR.exists():
        pc_items = []
        android_items = []
        crossplatform_items = []

        pc_file = ADS_DIR / "pc.yaml"
        android_file = ADS_DIR / "android.yaml"
        crossplatform_file = ADS_DIR / "crossplatform.yaml"

        if pc_file.exists():
            print(f"📄 Ads PC: {pc_file.name}")
            pc_items = extract_items_from_yaml(pc_file)

        if android_file.exists():
            print(f"📄 Ads Android: {android_file.name}")
            android_items = extract_items_from_yaml(android_file)

        if crossplatform_file.exists():
            print(f"📄 Ads Crossplatform: {crossplatform_file.name}")
            crossplatform_items = extract_items_from_yaml(crossplatform_file)

        # ads_pc.mrs = pc + crossplatform
        ads_pc = merge_unique(pc_items, crossplatform_items)
        convert_to_mrs(ads_pc, MRS_DIR / "ads_pc.mrs")

        # ads_mobile.mrs = android + crossplatform
        ads_mobile = merge_unique(android_items, crossplatform_items)
        convert_to_mrs(ads_mobile, MRS_DIR / "ads_mobile.mrs")

        # Обрабатываем другие YAML в ads/ (если появятся)
        for yaml_file in sorted(ADS_DIR.glob("*.yaml")):
            if yaml_file.name in ("pc.yaml", "android.yaml", "crossplatform.yaml"):
                continue
            print(f"📄 Ads прочее: {yaml_file.name}")
            output_name = f"ads_{yaml_file.stem}.mrs"
            convert_to_mrs(extract_items_from_yaml(yaml_file), MRS_DIR / output_name)

    # Direct
    direct_file = RULES_ROOT / "direct.yaml"
    if direct_file.exists():
        print(f"📄 Direct: {direct_file.name}")
        convert_to_mrs(extract_items_from_yaml(direct_file), MRS_DIR / "direct.mrs")

    # Proxy
    proxy_file = RULES_ROOT / "proxy.yaml"
    if proxy_file.exists():
        print(f"📄 Proxy: {proxy_file.name}")
        convert_to_mrs(extract_items_from_yaml(proxy_file), MRS_DIR / "proxy.mrs")

    # Другие YAML (кроме ads/ и programs/)
    for yaml_file in sorted(RULES_ROOT.rglob("*.yaml")):
        if ADS_DIR in yaml_file.parents:
            continue
        if PROGRAMS_DIR in yaml_file.parents:
            continue
        if yaml_file.name in ("direct.yaml", "proxy.yaml"):
            continue

        print(f"📄 Прочее: {yaml_file.relative_to(RULES_ROOT)}")
        output_name = yaml_file.stem + ".mrs"
        convert_to_mrs(extract_items_from_yaml(yaml_file), MRS_DIR / output_name)

    print("\n✅ Все конвертации завершены")
    print(f"📦 Результаты в {MRS_DIR}/")
    print(f"ℹ️ Programs (rules/programs/) не конвертируются — используются напрямую как YAML")

if __name__ == "__main__":
    main()
