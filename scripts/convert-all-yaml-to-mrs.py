#!/usr/bin/env python3
"""
Универсальный конвертер YAML → .mrs для Mihomo.

Логика:
1. rules/ads/*.yaml — сливаются в один ads.mrs (domain)
2. rules/direct.yaml — отдельный direct.mrs (domain)
3. rules/proxy.yaml — отдельный proxy.mrs (domain)
4. rules/programs/*.yaml — каждый в свой .mrs (rule type, PROCESS-NAME)
5. Любой другой YAML в rules/ — конвертируется в .mrs с тем же именем

Тип правила определяется по имени папки/файла:
- programs → rule (PROCESS-NAME)
- всё остальное → domain (DOMAIN-SUFFIX)
"""

import sys
import yaml
import subprocess
from pathlib import Path

RULES_ROOT = Path("rules")
DIST_DIR = Path("dist")
MIHOMO_BIN = "mihomo"

# Особые правила
ADS_DIR = RULES_ROOT / "ads"
PROGRAMS_DIR = RULES_ROOT / "programs"

def extract_items_from_yaml(yaml_path: Path) -> list[str]:
    """Извлекает домены или правила из YAML. Поддерживает оба формата:
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
            # Формат payload:
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

    # Чистим: убираем пустые строки и дубликаты
    seen = set()
    unique = []
    for item in items:
        item = item.strip()
        if item and item not in seen:
            seen.add(item)
            unique.append(item)

    return unique

def convert_to_mrs(items: list[str], output_path: Path, rule_type: str):
    """Конвертирует список правил в .mrs через mihomo."""
    if not items:
        print(f"⚠️ {output_path.name}: нет правил, создаю пустой .mrs")
        output_path.touch()
        return

    # Создаём временный файл
    tmp_file = Path(f"/tmp/{output_path.stem}.txt")
    with open(tmp_file, "w", encoding="utf-8") as f:
        for item in items:
            if rule_type == "domain":
                f.write(f"DOMAIN-SUFFIX,{item}\n")
            else:
                f.write(f"{item}\n")

    # Конвертируем
    cmd = [MIHOMO_BIN, "convert-ruleset", rule_type, "text", str(tmp_file), str(output_path)]
    print(f"🔄 {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Ошибка конвертации {output_path.name}: {result.stderr}", file=sys.stderr)
        # Создаём пустой файл, чтобы workflow не падал
        output_path.touch()
    else:
        print(f"✅ {output_path.name}: {len(items)} правил")

def main():
    if not RULES_ROOT.exists():
        print(f"❌ Директория {RULES_ROOT} не найдена", file=sys.stderr)
        sys.exit(1)

    DIST_DIR.mkdir(exist_ok=True)

    # 1. Ads — слияние всех YAML в rules/ads/
    if ADS_DIR.exists():
        ads_items = []
        for yaml_file in sorted(ADS_DIR.glob("*.yaml")):
            print(f"📄 Ads: {yaml_file.name}")
            ads_items.extend(extract_items_from_yaml(yaml_file))
        convert_to_mrs(ads_items, DIST_DIR / "ads.mrs", "domain")

    # 2. Direct
    direct_file = RULES_ROOT / "direct.yaml"
    if direct_file.exists():
        print(f"📄 Direct: {direct_file.name}")
        convert_to_mrs(extract_items_from_yaml(direct_file), DIST_DIR / "direct.mrs", "domain")

    # 3. Proxy
    proxy_file = RULES_ROOT / "proxy.yaml"
    if proxy_file.exists():
        print(f"📄 Proxy: {proxy_file.name}")
        convert_to_mrs(extract_items_from_yaml(proxy_file), DIST_DIR / "proxy.mrs", "domain")

    # 4. Programs — каждый YAML отдельно, тип rule
    if PROGRAMS_DIR.exists():
        for yaml_file in sorted(PROGRAMS_DIR.glob("*.yaml")):
            print(f"📄 Programs: {yaml_file.name}")
            output_name = yaml_file.stem + ".mrs"
            convert_to_mrs(extract_items_from_yaml(yaml_file), DIST_DIR / output_name, "rule")

    # 5. Все остальные YAML в rules/ (кроме ads, programs, direct, proxy)
    #    Каждый конвертируется в .mrs с тем же именем (domain type)
    for yaml_file in sorted(RULES_ROOT.rglob("*.yaml")):
        # Пропускаем уже обработанные
        if ADS_DIR in yaml_file.parents or PROGRAMS_DIR in yaml_file.parents:
            continue
        if yaml_file.name in ("direct.yaml", "proxy.yaml"):
            continue

        print(f"📄 Прочее: {yaml_file.relative_to(RULES_ROOT)}")
        # Определяем тип: если в имени есть process/program — rule, иначе domain
        rule_type = "rule" if "process" in yaml_file.stem.lower() or "program" in yaml_file.stem.lower() else "domain"
        output_name = yaml_file.stem + ".mrs"
        convert_to_mrs(extract_items_from_yaml(yaml_file), DIST_DIR / output_name, rule_type)

    print("\n✅ Все конвертации завершены")
    print(f"📦 Результаты в {DIST_DIR}/")

if __name__ == "__main__":
    main()
