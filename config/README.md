# ⚙️ AtlasTrinity Configuration

Конфігураційні файли системи з **автоматичною синхронізацією**.

## 📁 Файли

| Файл | Опис | Sync Mode |
|------|------|-----------|
| `config.yaml` | Головний конфіг системи | Smart Merge |
| `config_sync.py` | Утиліта синхронізації | - |

### config.yaml
Головний конфігураційний файл системи. Містить налаштування:

- **Agents**: Atlas (raptor-mini), Tetyana (gpt-4.1), Grisha (gpt-4o)
- **MCP Servers**: Terminal, Filesystem, Playwright, Computer Use, Whisper
- **Voice**: TTS (ukrainian-tts), STT (Whisper turbo на MPS)
- **Security**: Небезпечні команди, підтвердження
- **Logging**: Рівень, розмір файлів

> **Примітка**: TTS тренувальний конфіг (`config.yaml` для ukrainian-tts моделі) 
> знаходиться в `~/.config/atlastrinity/models/tts/config.yaml` і завантажується 
> автоматично бібліотекою ukrainian-tts.

## 🔄 Синхронізація

### Двостороння синхронізація
```
config/                      ←→    ~/.config/atlastrinity/
├── config.yaml             MERGE   ├── config.yaml
└── (src/mcp/config.json)   COPY    └── mcp/config.json
```

### Команди
```bash
# Показати статус
python config/config_sync.py status

# Синхронізувати обидва напрямки (рекомендовано)
python config/config_sync.py sync

# Проект → Глобальна (push нові ключі, зберегти user values)
python config/config_sync.py push

# Глобальна → Проект (pull user values)
python config/config_sync.py pull
```

### Smart Merge Logic
1. **СТРУКТУРА** береться з проекту (нові ключі додаються)
2. **ЗНАЧЕННЯ** зберігаються з глобальної (user customization)
3. При оновленні бінарника користувач отримує нові ключі

### При оновленні .app (production)
Автоматично виконується smart merge:
- ✅ Нові ключі з bundle ДОДАЮТЬСЯ
- ✅ Існуючі значення користувача ЗБЕРІГАЮТЬСЯ
- ✅ `.env` НЕ перезаписується (API ключі)
- ✅ `mcp/config.json` ОНОВЛЮЄТЬСЯ (системний конфіг)

## 📍 Розташування

### Development
- **Project**: `config/config.yaml` (source of truth for structure)
- **Global**: `~/.config/atlastrinity/config.yaml` (runtime + user values)

### Production (.app)
- **Bundle**: `AtlasTrinity.app/Contents/Resources/config.yaml`
- **Global**: `~/.config/atlastrinity/config.yaml`

## 🎯 Workflow

### Як додати новий параметр
```bash
# 1. Редагуй config/config.yaml в проекті
vim config/config.yaml

# 2. Синхронізуй (push нові ключі в глобальну)
python config/config_sync.py push

# 3. Перезапусти систему
npm run dev
```

### Як отримати зміни з глобальної папки
```bash
# Якщо редагував ~/.config/atlastrinity/config.yaml
python config/config_sync.py pull

# Commit changes
git add config/config.yaml
git commit -m "feat: sync user config changes"
```

## 📝 Приклад (Whisper на MPS)

```yaml
voice:
  tts:
    device: "cpu"     # TTS стабільно на CPU
    enabled: true     # Увімкнути TTS
  
  stt:
    model: "turbo"    # Оптимізована large-v3 (809MB)
    language: "uk"    # Українська мова
    device: "mps"     # Apple Silicon GPU (14x швидше!)
```

## 🔗 Структура ~/.config/atlastrinity/

```
~/.config/atlastrinity/
├── .env                    # API ключі (НЕ перезаписується)
├── config.yaml             # Системний конфіг (SMART MERGE)
├── config.yaml.backup      # Backup перед sync
├── logs/
│   └── brain.log
├── memory/
├── screenshots/
├── mcp/
│   └── config.json         # MCP servers (ПЕРЕЗАПИСУЄТЬСЯ)
└── models/
    ├── tts/                # TTS моделі (auto-download)
    └── whisper/            # Whisper моделі (auto-download)
```

- [CONFIG_ARCHITECTURE.md](../docs/CONFIG_ARCHITECTURE.md) - Детальна архітектура
- [Setup Guide](../SETUP.md) - Налаштування середовища
- [Documentation](../docs/)
