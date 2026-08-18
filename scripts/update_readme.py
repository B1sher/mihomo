#!/usr/bin/env python3
"""
Обновляет README.md — вставляет автоматически сгенерированные
raw-ссылки на .mrs файлы (из ветки mrs) и .yaml файлы (из programs/).

Единая таблица: Файл | Тип | Обновлён
Имя файла кликабельное, без расширения.
"""

import re
from datetime import datetime, timezone
from pathlib import Path

REPO = "B1sher/mihomo"
MRS_BRANCH = "mrs"
MAIN_BRANCH = "main"

PROGRAMS_DIR = Path("rules/programs")
README_PATH = Path("README.md")

LINKS_START = "<!-- LINKS_START -->"
LINKS_END = "<!-- LINKS_END -->"

MRS_FILES = [
    "ads_pc.mrs",
    "ads_phone.mrs",
    "direct.mrs",
    "proxy.mrs",
]

def get_current_time():
    """Возвращает время в формате ЧЧ:ММ ДД.ММ.ГГ (UTC)."""
    now = datetime.now(timezone.utc)
    return now.strftime("%H:%M %d.%m.%y")

def generate_unified_table():
    """Генерирует единую таблицу с .mrs и .yaml файлами."""
    time
