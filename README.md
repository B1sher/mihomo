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
│       → ads_pc.mrs
│       → ads_phone.mrs
│
├── programs/                       # Программы и игры (PROCESS-NAME)
│   ├── programs_pc_direct.yaml     # 🎮 ПК — процессы напрямую
│   ├── programs_pc_proxy.yaml      # 🔀 ПК — процессы через прокси
│   ├── programs_phone_direct.yaml  # 📱 Телефон — приложения напрямую
│   └── programs_phone_proxy.yaml   # 📱 Телефон — приложения через прокси
│
├── direct.yaml                     # 🌐 Домены и IP прямо
│   ↓ (конвертация в mrs)
│   → direct.mrs
│
└── proxy.yaml                      # 🔀 Домены и IP через прокси
    ↓ (конвертация в mrs)
    → proxy.mrs

```
`.mrs` файлы генерятся автоматически в отдельную ветку `mrs` при каждом пуше  
raw-ссылки ниже так же создаются автоматически:

## Raw-ссылки

<!-- MRS_LINKS_START -->
| Файл | Ссылка |
|------|--------|
| `ads_pc.mrs` | <details><summary>📋 Копировать</summary><code>https://raw.githubusercontent.com/B1sher/mihomo/mrs/ads_pc.mrs</code></details> |
| `ads_phone.mrs` | <details><summary>📋 Копировать</summary><code>https://raw.githubusercontent.com/B1sher/mihomo/mrs/ads_phone.mrs</code></details> |
| `direct.mrs` | <details><summary>📋 Копировать</summary><code>https://raw.githubusercontent.com/B1sher/mihomo/mrs/direct.mrs</code></details> |
| `proxy.mrs` | <details><summary>📋 Копировать</summary><code>https://raw.githubusercontent.com/B1sher/mihomo/mrs/proxy.mrs</code></details> |
<!-- MRS_LINKS_END -->
<hr style="opacity: 0.3;">
<!-- YAML_LINKS_START -->
| Файл | Ссылка |
|------|--------|
| `programs_pc_direct.yaml` | <details><summary>📋 Копировать</summary><code>https://raw.githubusercontent.com/B1sher/mihomo/main/rules/programs/programs_pc_direct.yaml</code></details> |
| `programs_pc_proxy.yaml` | <details><summary>📋 Копировать</summary><code>https://raw.githubusercontent.com/B1sher/mihomo/main/rules/programs/programs_pc_proxy.yaml</code></details> |
| `programs_phone_direct.yaml` | <details><summary>📋 Копировать</summary><code>https://raw.githubusercontent.com/B1sher/mihomo/main/rules/programs/programs_phone_direct.yaml</code></details> |
| `programs_phone_proxy.yaml` | <details><summary>📋 Копировать</summary><code>https://raw.githubusercontent.com/B1sher/mihomo/main/rules/programs/programs_phone_proxy.yaml</code></details> |
<!-- YAML_LINKS_END -->




## Формат YAML

### Домены, IP и подсети (classical)

В `direct.yaml`, `proxy.yaml`, `ads/*.yaml` сейчас только домены.  
Что бы писать вперемешку, нужно в `rule-providers` указать `behavior: classical`

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

| Источник | Type | Behavior | Format | Выход |
|----------|------|----------|--------|-------|
| `rules/ads/*.yaml` | http | domain | mrs | `mrs/ads_pc.mrs` и `mrs/ads_mobile.mrs` |
| `rules/direct.yaml` | http | domain | mrs | `mrs/direct.mrs` |
| `rules/proxy.yaml` | http | domain | mrs | `mrs/proxy.mrs` |
| `rules/programs/*.yaml` | http | classical | yaml | не изменяется |
| Любой новый YAML | http | любой | mrs | `mrs/<имя>.mrs` |

Важно:
Если в списке ads/direct/proxy 

>только домены, то в rule-providers нужно указывать `behavior: domain`  
>если только подсети, то `behavior: ipcidr`  
>если и то, и другое, то `behavior: classical`


Иначе не читает >:(  
В `programs` с процессами `только yaml`
