#!/usr/bin/env python3
"""
Универсальный конвертер YAML → .mrs для Mihomo.

Поддерживает в одном YAML:
- Домены: example.com → DOMAIN-SUFFIX,example.com
- Подсети: 192.168.1.0/24 → IP-CIDR,192.168.1.0/24
- IP: 1.1.1.1 → IP-CIDR,1.1.1.1/32
- Процессы: PROCESS-NAME,... (для rules/programs/)

Логика:
1. rules/ads/*.yaml — сливаются в один ads.mrs (classical)
2. rules/direct.yaml — direct.mrs (classical)
3. rules/proxy.yaml — proxy.mrs (classical)
4. rules/programs/*.yaml — каждый в свой .mrs (rule type)
5. Любой другой YAML — конвертируется в .mrs с тем же именем
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

    # Если это PROCESS-NAME правило (содержит PROCESS-NAME)
    if item.upper().startswith("PROCESS-NAME"):
        return item

    # Если это IP или подсеть (содержит только цифры, точки и /)
    if "/" in item:
        # Проверяем, похоже ли на CIDR
        try:
            ipaddress.ip_network(item, strict=False)
            return f"IP-CIDR,{item}"
        except ValueError:
            pass
    else:
        # Проверяем, не чистый ли это IP
        try:
            ipaddress.ip_address(item)
            return f"IP-CIDR,{item}/32"
        except ValueError:
            pass

    # Всё остальное считаем доменом
    return f"DOMAIN-SUFFIX,{item}"

def extract_items_from_yaml(yaml_path: Path) -> list[str]:
    """Извлекает элементы из YAML. Поддерживает:
    - Список строк: - "domain.com"
    - payload: - PROCESS-NAME,...
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

    # Классифицируем и убираем дубликаты
    seen = set()
    unique = []
    for item in items:
        rule = classify_item(item)
        if rule and rule not in seen:
            seen.add(rule)
            unique.append(rule)

    return unique

def convert_to_mrs(items: list[str], output_path: Path, rule_type: str):
    """Конвертирует список правил в .mrs через mihomo."""
    if not items:
        print(f"⚠️ {output_path.name}: нет правил, создаю пустой .mrs")
        output_path.touch()
        return

    tmp_file = Path(f"/tmp/{output_path.stem}.txt")
    with open(tmp_file, "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"{item}\n")

    cmd = [MIHOMO_BIN, "convert-ruleset", rule_type, "text", str(tmp_file), str(output_path)]
    print(f"🔄 {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Ошибка конвертации {output_path.name}: {result.stderr}", file=sys.stderr)
        output_path.touch()
    else:
        print(f"✅ {output_path.name}: {len(items)} правил")

def main():
    if not RULES_ROOT.exists():
        print(f"❌ Директория {RULES_ROOT} не найдена", file=sys.stderr)
        sys.exit(1)

    DIST_DIR.mkdir(exist_ok=True)

    # 1. Ads — слияние всех YAML в rules/ads/ (classical — поддерживает домены и IP)
    if ADS_DIR.exists():
        ads_items = []
        for yaml_file in sorted(ADS_DIR.glob("*.yaml")):
            print(f"📄 Ads: {yaml_file.name}")
            ads_items.extend(extract_items_from_yaml(yaml_file))
        convert_to_mrs(ads_items, DIST_DIR / "ads.mrs", "classical")

    # 2. Direct — domain и IP (classical)
    direct_file = RULES_ROOT / "direct.yaml"
    if direct_file.exists():
        print(f"📄 Direct: {direct_file.name}")
        convert_to_mrs(extract_items_from_yaml(direct_file), DIST_DIR / "direct.mrs", "classical")

    # 3. Proxy — domain и IP (classical)
    proxy_file = RULES_ROOT / "proxy.yaml"
    if proxy_file.exists():
        print(f"📄 Proxy: {proxy_file.name}")
        convert_to_mrs(extract_items_from_yaml(proxy_file), DIST_DIR / "proxy.mrs", "classical")

    # 4. Programs — PROCESS-NAME (rule)
    if PROGRAMS_DIR.exists():
        for yaml_file in sorted(PROGRAMS_DIR.glob("*.yaml")):
            print(f"📄 Programs: {yaml_file.name}")
            output_name = yaml_file.stem + ".mrs"
            convert_to_mrs(extract_items_from_yaml(yaml_file), DIST_DIR / output_name, "rule")

    # 5. Все остальные YAML — classical (домены + IP)
    for yaml_file in sorted(RULES_ROOT.rglob("*.yaml")):
        if ADS_DIR in yaml_file.parents or PROGRAMS_DIR in yaml_file.parents:
            continue
        if yaml_file.name in ("direct.yaml", "proxy.yaml"):
            continue

        print(f"📄 Прочее: {yaml_file.relative_to(RULES_ROOT)}")
        output_name = yaml_file.stem + ".mrs"
        convert_to_mrs(extract_items_from_yaml(yaml_file), DIST_DIR / output_name, "classical")

    print("\n✅ Все конвертации завершены")
    print(f"📦 Результаты в {DIST_DIR}/")

if __name__ == "__main__":
    main()
