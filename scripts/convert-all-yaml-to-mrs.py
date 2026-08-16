#!/usr/bin/env python3
"""
Универсальный конвертер YAML → .mrs для Mihomo.

Всё собирается как classical. Поддерживает:
- Домены: example.com → DOMAIN-SUFFIX,example.com
- Подсети: 192.168.1.0/24 → IP-CIDR,192.168.1.0/24
- IP: 1.1.1.1 → IP-CIDR,1.1.1.1/32
- Процессы: PROCESS-NAME,... (остаются как есть)
- Комментарии в конце строк: - PROCESS-NAME,foo.exe # comment → вырезаются
"""

import sys
import re
import ipaddress
import yaml
import subprocess
from pathlib import Path

RULES_ROOT = Path("rules")
DIST_DIR = Path("dist")
MIHOMO_BIN = "mihomo"

ADS_DIR = RULES_ROOT / "ads"
PROGRAMS_DIR = RULES_ROOT / "programs"

def strip_comment(item: str) -> str:
    """Вырезает комментарий # из строки."""
    # Если # внутри кавычек — не трогаем (упрощённо)
    if '#' in item:
        item = item.split('#')[0].strip()
    return item

def classify_item(item: str) -> str:
    """Определяет тип строки и возвращает готовое правило."""
    item = strip_comment(item.strip())
    if not item:
        return ""

    # PROCESS-NAME
    if item.upper().startswith("PROCESS-NAME"):
        return item

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
    """Извлекает элементы из YAML."""
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
    for item in items:
        rule = classify_item(item)
        if rule and rule not in seen:
            seen.add(rule)
            unique.append(rule)

    return unique

def convert_to_mrs(items: list[str], output_path: Path):
    """Конвертирует список правил в .mrs (classical)."""
    if not items:
        print(f"⚠️ {output_path.name}: нет правил, создаю пустой .mrs")
        output_path.touch()
        return

    tmp_file = Path(f"/tmp/{output_path.stem}.txt")
    with open(tmp_file, "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"{item}\n")

    cmd = [MIHOMO_BIN, "convert-ruleset", "classical", "text", str(tmp_file), str(output_path)]
    print(f"🔄 {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Ошибка конвертации {output_path.name}: {result.stderr}", file=sys.stderr)
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

    # Ads
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

    # Programs
    if PROGRAMS_DIR.exists():
        for yaml_file in sorted(PROGRAMS_DIR.glob("*.yaml")):
            print(f"📄 Programs: {yaml_file.name}")
            output_name = yaml_file.stem + ".mrs"
            convert_to_mrs(extract_items_from_yaml(yaml_file), DIST_DIR / output_name)

    # Остальные
    for yaml_file in sorted(RULES_ROOT.rglob("*.yaml")):
        if ADS_DIR in yaml_file.parents or PROGRAMS_DIR in yaml_file.parents:
            continue
        if yaml_file.name in ("direct.yaml", "proxy.yaml"):
            continue
        print(f"📄 Прочее: {yaml_file.relative_to(RULES_ROOT)}")
        output_name = yaml_file.stem + ".mrs"
        convert_to_mrs(extract_items_from_yaml(yaml_file), DIST_DIR / output_name)

    print("\n✅ Все конвертации завершены")
    print(f"📦 Результаты в {DIST_DIR}/")

if __name__ == "__main__":
    main()
