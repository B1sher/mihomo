```

rules/
├── ads/                            # Рекламные и трекерные домены (REJECT)
│   ├── pc.yaml                     # 💻 Windows
│   ├── android.yaml                # 📱 Мобилки
│   └── crossplatform.yaml          # ⛔ Кроссплатформа
│       ↓ (слияние)                 
│       ↓ (конвертация в mrs)       # оба содержат кроссплатформу
│       ├─> ads_pc.mrs
│       └─> ads_phone.mrs
│
├── direct.yaml                     # 🌐 Домены и IP прямо
│   ↓ (конвертация в mrs)
│   └─> direct.mrs
│
├── proxy.yaml                      # 🔀 Домены и IP через прокси
│   ↓ (конвертация в mrs)
│   └─> proxy.mrs
│
└── apps/                           # Приложения и игры (PROCESS-NAME)
    ├── apps_pc_direct.yaml         # 🎮 ПК — процессы напрямую
    ├── apps_pc_proxy.yaml          # 🔀 ПК — процессы через прокси
    ├── apps_phone_direct.yaml      # 📱 Телефон — приложения напрямую
    └── apps_phone_proxy.yaml       # 📱 Телефон — приложения через прокси

```
>`.mrs` и `.yaml` файлы генерятся автоматически в отдельную ветку `lists` при каждом пуше  
>raw-ссылки ниже так же создаются автоматически:

## Raw-ссылки

<!-- LINKS_START -->

| Файл | Формат | Время (UTC+3) | Дата |
|------|--------|---------------|------|
| [ads_pc](https://raw.githubusercontent.com/B1sher/mihomo/lists/ads_pc.mrs) | `mrs` | 10:56 | 22.08.26 |
| [ads_phone](https://raw.githubusercontent.com/B1sher/mihomo/lists/ads_phone.mrs) | `mrs` | 10:56 | 22.08.26 |
| [direct](https://raw.githubusercontent.com/B1sher/mihomo/lists/direct.mrs) | `mrs` | 10:56 | 22.08.26 |
| [proxy](https://raw.githubusercontent.com/B1sher/mihomo/lists/proxy.mrs) | `mrs` | 10:56 | 22.08.26 |
| [apps_pc_direct](https://raw.githubusercontent.com/B1sher/mihomo/main/rules/apps/apps_pc_direct.yaml) | `yaml` | 10:56 | 22.08.26 |
| [apps_pc_proxy](https://raw.githubusercontent.com/B1sher/mihomo/main/rules/apps/apps_pc_proxy.yaml) | `yaml` | 10:56 | 22.08.26 |
| [apps_phone_direct](https://raw.githubusercontent.com/B1sher/mihomo/main/rules/apps/apps_phone_direct.yaml) | `yaml` | 10:56 | 22.08.26 |
| [apps_phone_proxy](https://raw.githubusercontent.com/B1sher/mihomo/main/rules/apps/apps_phone_proxy.yaml) | `yaml` | 10:56 | 22.08.26 |

<!-- LINKS_END -->

### Домены, IP и подсети (.mrs)

В `direct.yaml`, `proxy.yaml`, `ads/*.yaml` сейчас только домены.  
Что бы писать вперемешку, нужно в `rule-providers` указать `behavior: classical`  

```yaml
# Домен (behavior: domain)
- "example.com"
- DOMAIN,example.com
- DOMAIN-SUFFIX,example.com

# Подсеть (behavior: ipcidr)
- "192.168.1.0/24"
- IP-CIDR,192.168.1.0/24

# Одиночный IP
- "1.1.1.1"
- IP-CIDR,1.1.1.1/32

# Вперемешку (behavior: classical)
```
>Можно заполнять любым форматом из указанных, при конвертации в `.mrs` он допишет правила,  
>но лучше соблюдать полный формат с указанием правил и `payload:` для универсальности.

### Процессы (.yaml)

В `apps/*.yaml` процессы приложений.

```yaml
# Точное совпадение имени процесса
  - PROCESS-NAME,Discord.exe                  # 💻 Windows
  - PROCESS-NAME,discord                      # 🐧 Linux
  - PROCESS-NAME,com.google.android.youtube   # 📱 Android

# Ищет любые процессы содержащие это имя + любые подпроцессы если на конце *
  - PROCESS-NAME-WILDCARD,com.google.android.youtube*

# То же самое, но мощнее (игнорит регистр и любые символы)
# в примере применяется для всего, где упоминается youtube
  - PROCESS-NAME-REGEX,(?i).*youtube.*
```

## Сборка

Один workflow автоматически конвертирует все YAML в `rules/` при пуше, кроме `rules/apps/`:

| Источник | Type | Behavior | Format | Выход |
|----------|------|----------|--------|-------|
| `rules/ads/*.yaml` | http | domain | mrs/yaml | `ads_pc.mrs/yaml` и `ads_mobile.mrs/yaml` |
| `rules/direct.yaml` | http | domain | mrs | `direct.mrs` |
| `rules/proxy.yaml` | http | domain | mrs | `proxy.mrs` |
| `rules/apps/*.yaml` | http | classical | yaml | не изменяется |
| Любой новый YAML | http | любой | mrs | `<имя>.mrs` |

Важно:
Если в списке ads/direct/proxy 

>только домены, то в rule-providers нужно указывать `behavior: domain`  
>если только подсети, то `behavior: ipcidr`  
>если и то, и другое, то `behavior: classical` (работает медленнее)

В `apps` с процессами `только yaml` + в нём `payload:` + для правил `(behavior: classical)`
