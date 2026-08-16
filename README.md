# 🛡️ Personal Mih
```

📁 repo/
├── rules/
│   ├── ads/
│   │   ├── pc.yaml              ← 💻 PC телеметрия
│   │   ├── android.yaml         ← 📱 Android реклама/трекеры
│   │   └── crossplatform.yaml   ← ⛔ Кроссплатформенная реклама
│   ├── programs/
│   │   ├── programs_direct.yaml ← 🎮 Программы напрямую (PROCESS-NAME)
│   │   └── programs_proxy.yaml  ← 🔀 Программы через прокси (PROCESS-NAME)
│   ├── direct.yaml              ← 🌐 Домены для прямого подключения
│   └── proxy.yaml               ← 🔀 Домены через прокси
├── scripts/
│   └── convert-all-yaml-to-mrs.py
├── .github/workflows/
│   └── build-all-mrs.yml
└── dist/
├── ads.mrs
├── direct.mrs
├── proxy.mrs
├── programs_direct.mrs
└── programs_proxy.mrs

```

## 🔧
```

### Rule (PROCESS-NAME) rules

```
rule-prov
```

## ✏️ Форматы YAML

### Domain (обычные домены)

```

```

### Rule (PROCESS-NAME)

```
payload:
  - PROCESS-NAME
```

## ℹ️ Примечание

- `ads/` — все YAML сливаются в один `ads.mrs`
- `programs/` — каждый YAML даёт отдельный .mrs
- Новые YAML в других подпапках обрабатываются автоматически
- Пустые YAML создают пустой .mrs (без ошибок)

```

</B
```

Теперь при добавлении любого нового YAML в `rules/` — он подхватится без правок workflow. 🚀
