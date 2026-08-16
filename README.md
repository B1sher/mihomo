# Mihomo Rules

## Дерево проекта

```

rules/
├── ads/                          # Рекламные и трекерные домены (REJECT)
│   ├── pc.yaml                   # 💻 Windows
│   ├── android.yaml              # 📱 Мобилки
│   └── crossplatform.yaml        # ⛔ Кроссплатформа
│       ↓ (слияние)
│       → dist/ads.mrs
│
├── programs/                     # Программы и игры (PROCESS-NAME)
│   ├── programs_pc_direct.yaml   # 🎮 ПК — процессы напрямую
│   │   → dist/programs_pc_direct.mrs
│   ├── programs_pc_proxy.yaml    # 🔀 ПК — процессы через прокси
│   │   → dist/programs_pc_proxy.mrs
│   ├── programs_phone_direct.yaml # 📱 Телефон — приложения напрямую
│   │   → dist/programs_phone_direct.mrs
│   └── programs_phone_proxy.yaml  # 📱 Телефон — приложения через прокси
│       → dist/programs_phone_proxy.mrs
│
├── direct.yaml                   # 🌐 Домены и IP прямо
│   → dist/direct.mrs
│
└── proxy.yaml                    # 🔀 Домены и IP через прокси
→ dist/proxy.mrs

```

## Формат YAML

### Домены, IP и подсети (classical)

В `direct.yaml`, `proxy.yaml`, `ads/*.yaml` можно писать вперемешку:

```yaml
# Домен
- "example.com"           # → DOMAIN-SUFFIX,example.com

# Подсеть
- "192.168.1.0/24"        # → IP-CIDR,192.168.1.0/24

# Одиночный IP
- "1.1.1.1"               # → IP-CIDR,1.1.1.1/32
```

### Процессы (rule, PROCESS-NAME)

В `programs/*.yaml`:

```
payload:
  - PROCESS-NAME,example.exe
  - PROCESS-NAME-REGEX,(?i).*Example.*
```

## Сборка

Один workflow автоматически конвертирует все YAML в `rules/` при пуше:

| Источник ↕▾ | Тип ↕▾ | Выход ↕▾ |
|---|---|---|
| −`rules/ads/*.yaml` | classical | `dist/ads.mrs` (слияние) |
| −`rules/direct.yaml` | classical | `dist/direct.mrs` |
| −`rules/proxy.yaml` | classical | `dist/proxy.mrs` |
| −`rules/programs/*.yaml` | rule | `dist/<имя>.mrs` |
| −Любой новый YAML | classical | `dist/<имя>.mrs` |
⚙

