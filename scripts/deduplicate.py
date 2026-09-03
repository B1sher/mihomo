#!/usr/bin/env python3
"""Удаляет дубликаты правил в объединённых YAML-файлах."""
from pathlib import Path

FILES = ["merged/ads_pc.yaml", "merged/ads_phone.yaml"]

for file in FILES:
    path = Path(file)
    if not path.exists():
        print(f"Skip: {file} not found")
        continue

    lines = path.read_text(encoding="utf-8").splitlines()
    seen_payload = False
    seen_rules = set()
    result = []

    for line in lines:
        stripped = line.strip()

        # Пропускаем подряд идущие пустые строки
        if stripped == "":
            if result and result[-1].strip() != "":
                result.append(line)
            elif not result:
                result.append(line)
            continue

        # Первый payload: оставляем, второй — пропускаем
        if stripped == "payload:":
            if not seen_payload:
                seen_payload = True
                result.append(line)
            continue

        # Заголовки-комментарии оставляем
        if stripped.startswith("#"):
            result.append(line)
            continue

        # Правила — дедупликация по содержимому
        if line not in seen_rules:
            seen_rules.add(line)
            result.append(line)

    path.write_text("\n".join(result), encoding="utf-8")
    print(f"OK: {file} deduplicated")