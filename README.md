# Mihomo Rules

## Дерево проекта

```

rules/
├── ads/                            # Рекламные и трекерные домены (REJECT)
│   ├── pc.yaml                     # 💻 Windows
│   ├── android.yaml                # 📱 Мобилки
│   └── crossplatform.yaml          # ⛔ Кроссплатформа
│       ↓ (слияние)                 
│       ↓ (конвертация в mrs)       # оба содержат кроссплатформу
│       → mrs/ads_pc.mrs
│       → mrs/ads_phone.mrs
│
├── programs/                       # Программы и игры (PROCESS-NAME)
│   ├── programs_pc_direct.yaml     # 🎮 ПК — процессы напрямую
│   ├── programs_pc_proxy.yaml      # 🔀 ПК — процессы через прокси
│   ├── programs_phone_direct.yaml  # 📱 Телефон — приложения напрямую
│   └── programs_phone_proxy.yaml   # 📱 Телефон — приложения через прокси
│
├── direct.yaml                     # 🌐 Домены и IP прямо
│   ↓ (конвертация в mrs)
│   → mrs/direct.mrs
│
└── proxy.yaml                      # 🔀 Домены и IP через прокси
    ↓ (конвертация в mrs)
    → mrs/proxy.mrs

```

## Формат YAML

### Домены, IP и подсети (classical)

В `direct.yaml`, `proxy.yaml`, `ads/*.yaml` сейчас только домены.
>Что бы писать вперемешку, нужно в `rule-providers` указать `behavior: classical`

```yaml
# Домен
- "example.com"           # → DOMAIN-SUFFIX,example.com

# Подсеть
- "192.168.1.0/24"        # → IP-CIDR,192.168.1.0/24

# Одиночный IP
- "1.1.1.1"               # → IP-CIDR,1.1.1.1/32
```

### Процессы

В `programs/*.yaml`:

```
payload:
  - PROCESS-NAME,example.exe
  - PROCESS-NAME-REGEX,(?i).*Example.*
```

## Сборка

Один workflow автоматически конвертирует все YAML в `rules/` при пуше, кроме `rules/programs/`:

| Источник ↕▾ | Тип ↕▾ | Выход ↕▾ |
|---|---|---|
| −`rules/ads/*.yaml` | classical | `dist/ads.mrs` (слияние) |
| −`rules/direct.yaml` | classical | `dist/direct.mrs` |
| −`rules/proxy.yaml` | classical | `dist/proxy.mrs` |
| −`rules/programs/*.yaml` | yaml | `dist/<имя>.mrs` |
| −Любой новый YAML | classical | `dist/<имя>.mrs` |

Важно:
Если в списке ads/direct/proxy 

>только домены, то в rule-providers нужно указывать behavior: domain  
>если добавить туда подсети, то behavior: classical

Иначе не читает >:( 
В programs с процессами только yaml
