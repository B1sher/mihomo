# Mihomo Rules

## Дерево проекта

```

rules/
├── ads/                          # Рекламные и трекерные домены (блокировка)
│   ├── pc.yaml                   # 💻 Телеметрия Windows, драйверов, игровых лаунчеров
│   ├── android.yaml              # 📱 Мобильная реклама, трекеры приложений, телеметрия вендоров
│   └── crossplatform.yaml        # ⛔ Универсальные рекламные сети и аналитика
│       ↓ (слияние)
│       → dist/ads.mrs            # domain
│
├── programs/                     # Программы и игры (PROCESS-NAME)
│   ├── programs_pc_direct.yaml   # 🎮 ПК — процессы напрямую
│   │   → dist/programs_pc_direct.mrs     # rule
│   ├── programs_pc_proxy.yaml    # 🔀 ПК — процессы через прокси
│   │   → dist/programs_pc_proxy.mrs      # rule
│   ├── programs_phone_direct.yaml # 📱 Телефон — приложения напрямую
│   │   → dist/programs_phone_direct.mrs  # rule
│   └── programs_phone_proxy.yaml  # 📱 Телефон — приложения через прокси
│       → dist/programs_phone_proxy.mrs   # rule
│
├── direct.yaml                   # 🌐 Домены для прямого подключения
│   → dist/direct.mrs             # domain
│
└── proxy.yaml                    # 🔀 Домены через прокси
→ dist/proxy.mrs              # domain

```

## Сборка

Один workflow автоматически конвертирует все YAML в `rules/` при пуше:

| Источник | Тип | Выход |
|----------|-----|-------|
| `rules/ads/*.yaml` | domain | `dist/ads.mrs` (слияние) |
| `rules/direct.yaml` | domain | `dist/direct.mrs` |
| `rules/proxy.yaml` | domain | `dist/proxy.mrs` |
| `rules/programs/*.yaml` | rule | `dist/<имя>.mrs` (каждый отдельно) |
| Любой новый YAML | авто | `dist/<имя>.mrs` |
