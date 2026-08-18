#!/usr/bin/env python3
"""
Универсальный конвертер YAML → .mrs для Mihomo.

Поддерживает в одном YAML:
1. Простые домены: "example.com" → DOMAIN-SUFFIX,example.com
2. Подсети: "192.168.1.0/24" → IP-CIDR,192.168.1.0/24
3. IP: "1.1.1.1" → IP-CIDR,1.1.1.1/32
4. Готовые правила: DOMAIN-SUFFIX,example.com
5. Готовые IP-CIDR с параметрами: IP-CIDR,13.107.4.0/24,no-resolve
6. С payload: payload: - "example.com"

Оптимизация:
- Если в файле только домены → domain .mrs (быстрее в Mihomo)
- Если есть IP/подсети → classical .mrs (универсальный)
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

def classify_item(item: str) -> tuple[str, bool]:
    """Определяет тип строки.
    Возвращает (правило, has_ip) — has_ip=True если правило содержит IP/подсеть.
    """
    item = item.strip()
    if not item:
        return "", False

    # Уже готовое правило DOMAIN-SUFFIX,...
    if item.upper().startswith("DOMAIN-SUFFIX,"):
        return item, False

    # Уже готовое правило DOMAIN,...
    if item.upper().startswith("DOMAIN,"):
        return item, False

    # Уже готовое правило IP-CIDR,... (возможно с параметрами)
    if item.upper().startswith("IP-CIDR,"):
        return item, True

    # Уже готовое правило IP-CIDR6,...
    if item.upper().startswith("IP-CIDR6,"):
        return item, True

    # Прочие готовые правила (PROCESS-NAME, MATCH, и т.д.)
    if "," in item and not item.startswith("-"):
        # Определяем, есть ли IP в правиле
        has_ip = "IP-CIDR" in item.upper()
        return item, has_ip

    # Подсеть или IP
    if "/" in item:
        try:
            ipaddress.ip_network(item, strict=False)
            return f"IP-CIDR,{item}", True
        except ValueError:
            pass
    else:
        try:
            ipaddress.ip_address(item)
            return f"IP-CIDR,{item}/32", True
        except ValueError:
            pass

    # Домен
    return f"DOMAIN-SUFFIX,{item}", False

def extract_items_from_yaml(yaml_path: Path) -> tuple[list[str], bool]:
    """Извлекает правила из YAML.
    Возвращает (правила, has_ip) — has_ip=True если есть IP/подсети.
    """
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
            if "payload" in data and isinstance(data["payload"], list):
                for item in data["payload"]:
                    if isinstance(item, str):
                        items.append(item)
                    elif isinstance(item, dict):
                        items.extend(str(k) for k in item.keys())
            else:
                items.extend(str(k) for k in data.keys())
    except Exception as e:
        print(f"⚠️ Ошибка чтения {yaml_path}: {e}", file=sys.stderr)

    seen = set()
    unique = []
    has_ip = False
    for item in items:
        rule, item_has_ip = classify_item(item)
        if rule and rule not in seen:
            seen.add(rule)
            unique.append(rule)
            if item_has_ip:
                has_ip = True

    return unique, has_ip

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

def convert_to_mrs(items: list[str], output_path: Path, has_ip: bool = False):
    """Конвертирует правила в .mrs.
    Если has_ip=True → classical (универсальный).
    Если has_ip=False → domain (оптимизированный для доменов).
    """
    if not items:
        print(f"⚠️ {output_path.name}: нет правил, создаю пустой .mrs")
        output_path.touch()
        return

    tmp_file = Path(f"/tmp/{output_path.stem}.txt")
    with open(tmp_file, "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"{item}\n")

    # Выбираем тип конвертации
    if has_ip:
        behavior = "classical"
        print(f"📊 {output_path.name}: есть IP/подсети → classical")
    else:
        behavior = "domain"
        print(f"📊 {output_path.name}: только домены → domain (оптимизировано)")

    cmd = [MIHOMO_BIN, "convert-ruleset", behavior, "text", str(tmp_file), str(output_path)]
    print(f"🔄 {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Ошибка конвертации {output_path.name}: {result.stderr}", file=sys.stderr)
        output_path.touch()
    else:
        print(f"✅ {output_path.name}: {len(items)} правил ({behavior})")

def main():
    if not RULES_ROOT.exists():
        print(f"❌ Директория {RULES_ROOT} не найдена", file=sys.stderr)
        sys.exit(1)

    MRS_DIR.mkdir(exist_ok=True)

    # Ads — разделяем на PC и Mobile
    if ADS_DIR.exists():
        pc_items = []
        pc_has_ip = False
        android_items = []
        android_has_ip = False
        crossplatform_items = []
        crossplatform_has_ip = False

        pc_file = ADS_DIR / "pc.yaml"
        android_file = ADS_DIR / "android.yaml"
        crossplatform_file = ADS_DIR / "crossplatform.yaml"

        if pc_file.exists():
            print(f"📄 Ads PC: {pc_file.name}")
            pc_items, pc_has_ip = extract_items_from_yaml(pc_file)

        if android_file.exists():
            print(f"📄 Ads Android: {android_file.name}")
            android_items, android_has_ip = extract_items_from_yaml(android_file)

        if crossplatform_file.exists():
            print(f"📄 Ads Crossplatform: {crossplatform_file.name}")
            crossplatform_items, crossplatform_has_ip = extract_items_from_yaml(crossplatform_file)

        # ads_pc.mrs = pc + crossplatform
        ads_pc = merge_unique(pc_items, crossplatform_items)
        ads_pc_has_ip = pc_has_ip or crossplatform_has_ip
        convert_to_mrs(ads_pc, MRS_DIR / "ads_pc.mrs", ads_pc_has_ip)

        # ads_mobile.mrs = android + crossplatform
        ads_mobile = merge_unique(android_items, crossplatform_items)
        ads_mobile_has_ip = android_has_ip or crossplatform_has_ip
        convert_to_mrs(ads_mobile, MRS_DIR / "ads_mobile.mrs", ads_mobile_has_ip)

        # Другие YAML в ads/
        for yaml_file in sorted(ADS_DIR.glob("*.yaml")):
            if yaml_file.name in ("pc.yaml", "android.yaml", "crossplatform.yaml"):
                continue
            print(f"📄 Ads прочее: {yaml_file.name}")
            items, has_ip = extract_items_from_yaml(yaml_file)
            output_name = f"ads_{yaml_file.stem}.mrs"
            convert_to_mrs(items, MRS_DIR / output_name, has_ip)

    # Direct
    direct_file = RULES_ROOT / "direct.yaml"
    if direct_file.exists():
        print(f"📄 Direct: {direct_file.name}")
        items, has_ip = extract_items_from_yaml(direct_file)
        convert_to_mrs(items, MRS_DIR / "direct.mrs", has_ip)

    # Proxy
    proxy_file = RULES_ROOT / "proxy.yaml"
    if proxy_file.exists():
        print(f"📄 Proxy: {proxy_file.name}")
        items, has_ip = extract_items_from_yaml(proxy_file)
        convert_to_mrs(items, MRS_DIR / "proxy.mrs", has_ip)

    # Другие YAML (кроме ads/ и programs/)
    for yaml_file in sorted(RULES_ROOT.rglob("*.yaml")):
        if ADS_DIR in yaml_file.parents:
            continue
        if PROGRAMS_DIR in yaml_file.parents:
            continue
        if yaml_file.name in ("direct.yaml", "proxy.yaml"):
            continue

        print(f"📄 Прочее: {yaml_file.relative_to(RULES_ROOT)}")
        items, has_ip = extract_items_from_yaml(yaml_file)
        output_name = yaml_file.stem + ".mrs"
        convert_to_mrs(items, MRS_DIR / output_name, has_ip)

    print("\n✅ Все конвертации завершены")
    print(f"📦 Результаты в {MRS_DIR}/")
    print(f"ℹ️ Programs (rules/programs/) не конвертируются — используются напрямую как YAML")

if __name__ == "__main__":
    main()
