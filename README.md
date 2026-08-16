# 🛡️ Personal Mihomo Rules

Персональные правила, списки блокировок и конфигурация для [Mihomo](https://github.com/MetaCubeX/mihomo).

## 📁 Структура

```

📁 repo/
├── rules/
│   ├── ads/
│   │   ├── pc.yaml              ← 💻 PC телеметрия
│   │   ├── android.yaml         ← 📱 Android реклама/трекеры
│   │   └── crossplatform.yaml   ← ⛔ Кроссплатформенная реклама
│   ├── programs/
│   │   ├── programs_direct.yaml ← 🎮 Программы/игры напрямую (PROCESS-NAME)
│   │   └── programs_proxy.yaml  ← 🔀 Программы/игры через прокси (PROCESS-NAME)
│   ├── direct.yaml              ← 🌐 Домены для прямого подключения
│   └── proxy.yaml               ← 🔀 Домены через прокси
├── scripts/
│   ├── convert-yaml-to-mrs-ads.py
│   ├── convert-yaml-to-mrs-direct.py
│   ├── convert-yaml-to-mrs-proxy.py
│   ├── convert-yaml-to-mrs-programs-direct.py
│   └── convert-yaml-to-mrs-programs-proxy.py
├── .github/workflows/
│   ├── build-mrs-ads.yml
│   ├── build-mrs-direct.yml
│   ├── build-mrs-proxy.yml
│   ├── build-mrs-programs-direct.yml
│   └── build-mrs-programs-proxy.yml
└── dist/
├── ads.mrs
├── direct.mrs
├── proxy.mrs
├── programs_direct.mrs
└── programs_proxy.mrs

```

## 🔧 Сборка .mrs

| Файл | Тип | Формат |
|------|-----|--------|
| `ads.mrs` | domain | `DOMAIN-SUFFIX` |
| `direct.mrs` | domain | `DOMAIN-SUFFIX` |
| `proxy.mrs` | domain | `DOMAIN-SUFFIX` |
| `programs_direct.mrs` | classical | `PROCESS-NAME` / `PROCESS-NAME-REGEX` |
| `programs_proxy.mrs` | classical | `PROCESS-NAME` / `PROCESS-NAME-REGEX` |

## 📥 Использование в Mihomo

### Domain rules (ads, direct, proxy)

```yaml
rule-providers:
  ads:
    type: http
    behavior: domain
    url: "https://raw.githubusercontent.com/ВАШ_ЛОГИН/ВАШ_РЕПО/main/dist/ads.mrs"
    path: ./ruleset/ads.mrs
    interval: 86400
```

### Classical rules (programs_direct, programs_proxy)

```
rule-providers:
  programs-direct:
    type: http
    behavior: classical
    url: "https://raw.githubusercontent.com/ВАШ_ЛОГИН/ВАШ_РЕПО/main/dist/programs_direct.mrs"
    path: ./ruleset/programs_direct.mrs
    interval: 86400
```

## 🧠 Категории

### Ads (domain)

1. **PC 💻** — десктоп (Windows, драйверы, игры)
2. **Android 📱** — мобильные (реклама в приложениях, телеметрия вендоров)
3. **Кроссплатформа ⛔** — работает везде (рекламные сети, аналитика)

### Programs (classical, PROCESS-NAME)

- **programs_direct** — программы/игры для прямого подключения
- **programs_proxy** — программы/игры через прокси

### Direct / Proxy (domain)

- **direct** — домены для прямого подключения
- **proxy** — домены через прокси

## ✏️ Добавление домена (ads/direct/proxy)

Откройте нужный YAML и добавьте:

```
- "example.com" # Комментарий что это
```

## ✏️ Добавление процесса (programs)

Откройте нужный YAML в `rules/programs/` и добавьте в `payload:`:

```
payload:
  # Моя программа
  - PROCESS-NAME,myprogram.exe
  # Или по регулярному выражению
  - PROCESS-NAME-REGEX,(?i).*MyGame.*
```

