# 🔍 АНАЛІЗ: Whisper STT Інтеграція
## Дата: 2026-01-06 17:35

---

## 🎯 ПОТОЧНИЙ СТАН

### Whisper як Python пакет

**Встановлення**: `requirements.txt`
```
git+https://github.com/openai/whisper.git
```

✅ **Whisper встановлюється як Python пакет** (не бінарник)
- Встановлюється в `.venv/lib/python3.12/site-packages/whisper/`
- Production: копіюється в `dist_venv` → `.app/Contents/Resources/.venv/`

### Моделі Whisper

**Де зберігаються**: `~/.cache/whisper/`
```python
# whisper/__init__.py
def _download(url: str, root: str) -> str:
    os.makedirs(root, exist_ok=True)  # ~/.cache/whisper/
    ...
```

**Доступні моделі**:
- `tiny` - 39M parameters (~75MB)
- `base` - 74M parameters (~142MB) ✅ Default в config.yaml
- `small` - 244M parameters (~466MB)
- `medium` - 769M parameters (~1.5GB)
- `large-v3` - 1550M parameters (~3GB)

**Автозавантаження**: При першому `whisper.load_model("base")`
```python
# src/brain/voice/stt.py
@property
def model(self):
    if self._model is None:
        self._model = whisper.load_model(self.model_name, device=self.device)
    return self._model
```

---

## ⚠️ ПРОБЛЕМИ

### 1. Моделі НЕ в глобальній папці

**Поточне розташування**: `~/.cache/whisper/`
**Мало б бути**: `~/.config/atlastrinity/models/whisper/`

**Чому це проблема**:
- TTS моделі в `~/.config/atlastrinity/models/tts/` ✅
- STT моделі в `~/.cache/whisper/` ❌
- Неконсистентно!

### 2. Неможливо змінити download_root

**Код Whisper**:
```python
# whisper/__init__.py
def load_model(
    name: str,
    device: Optional[Union[str, torch.device]] = None,
    download_root: str = None,
    in_memory: bool = False,
) -> Whisper:
    if download_root is None:
        download_root = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
```

**Наш код**:
```python
# src/brain/voice/stt.py
self._model = whisper.load_model(self.model_name, device=self.device)
# ❌ Не передаємо download_root!
```

### 3. MCP Whisper Server

**Файл**: `src/mcp/whisper_server.py`

**Проблеми**:
- ❌ Не читає конфіг з `config.yaml`
- ❌ Хардкод `language="uk"`
- ❌ Не використовує config_loader

**Поточний код**:
```python
stt = WhisperSTT()  # Використовує defaults
```

**Має бути**:
```python
from src.brain.config_loader import config

mcp_config = config.get_mcp_config()
whisper_config = mcp_config.get("whisper", {})
model = whisper_config.get("model", "base")
language = whisper_config.get("language", "uk")

stt = WhisperSTT(model_name=model)
```

---

## ✅ РІШЕННЯ

### Варіант 1: Залишити ~/.cache/whisper/ (РЕКОМЕНДОВАНО)

**Плюси**:
- Стандартне розташування Whisper
- Не потребує модифікації коду
- Whisper community знає де шукати моделі

**Мінуси**:
- Не в `~/.config/atlastrinity/`
- Неконсистентно з TTS

**Реалізація**: Нічого не міняти, задокументувати

### Варіант 2: Перемістити в ~/.config/atlastrinity/models/whisper/

**Плюси**:
- Консистентно з TTS
- Всі моделі в одному місці
- Повний контроль

**Мінуси**:
- Треба модифікувати код
- Може конфліктувати з іншими застосунками

**Реалізація**:
```python
from ..config import CONFIG_ROOT

class WhisperSTT:
    @property
    def model(self):
        if self._model is None:
            download_root = CONFIG_ROOT / "models" / "whisper"
            download_root.mkdir(parents=True, exist_ok=True)
            
            self._model = whisper.load_model(
                self.model_name, 
                device=self.device,
                download_root=str(download_root)
            )
```

### Варіант 3: Гібрид (НАЙКРАЩИЙ)

**Ідея**: Symlink `~/.cache/whisper/` → `~/.config/atlastrinity/models/whisper/`

**Плюси**:
- Whisper думає що моделі в `~/.cache/`
- Фактично зберігаються в `~/.config/atlastrinity/`
- Консистентність + сумісність

**Реалізація**:
```python
# src/brain/config.py або setup_dev.py
import os
from pathlib import Path

def setup_whisper_symlink():
    """Створює symlink для Whisper моделей"""
    whisper_cache = Path.home() / ".cache" / "whisper"
    whisper_models = CONFIG_ROOT / "models" / "whisper"
    
    # Створюємо папку в config
    whisper_models.mkdir(parents=True, exist_ok=True)
    
    # Якщо ~/.cache/whisper не існує або не symlink
    if not whisper_cache.exists():
        whisper_cache.parent.mkdir(parents=True, exist_ok=True)
        whisper_cache.symlink_to(whisper_models)
        print(f"[Setup] Created symlink: {whisper_cache} → {whisper_models}")
```

---

## 🔧 РЕКОМЕНДОВАНІ ЗМІНИ

### 1. Додати download_root в STT (Варіант 2)

```python
# src/brain/voice/stt.py

from ..config import CONFIG_ROOT

class WhisperSTT:
    def __init__(self, model_name: str = None, device: str = None):
        stt_config = config.get("voice.stt", {})
        
        self.model_name = model_name or stt_config.get("model", "base")
        self.device = device
        self.language = stt_config.get("language", "uk")
        
        # Whisper моделі в глобальній папці
        self.download_root = CONFIG_ROOT / "models" / "whisper"
        self._model = None
    
    @property
    def model(self):
        if self._model is None and WHISPER_AVAILABLE:
            print(f"[STT] Loading Whisper model: {self.model_name}...")
            
            # Створюємо папку якщо не існує
            self.download_root.mkdir(parents=True, exist_ok=True)
            
            self._model = whisper.load_model(
                self.model_name, 
                device=self.device,
                download_root=str(self.download_root)  # ✅ Використовуємо глобальну папку
            )
            print(f"[STT] Model loaded from: {self.download_root}")
        return self._model
```

### 2. Інтегрувати config в MCP Whisper Server

```python
# src/mcp/whisper_server.py

from src.brain.config_loader import config

server = FastMCP("whisper-stt")

# Читаємо конфіг
mcp_config = config.get_mcp_config()
whisper_config = mcp_config.get("whisper", {})

# Ініціалізуємо з конфігу
try:
    model_name = whisper_config.get("model", "base")
    stt = WhisperSTT(model_name=model_name)
    print(f"[MCP Whisper] Initialized with model: {model_name}")
except Exception as e:
    print(f"[MCP Whisper] Failed to init STT: {e}")
    stt = None

@server.tool()
def transcribe_audio(audio_path: str, language: str = None) -> str:
    """Transcribe an audio file to text."""
    if not stt:
        return "STT Init Failed"
    
    # Використовуємо language з конфігу якщо не вказано
    if language is None:
        language = whisper_config.get("language", "uk")
    
    result = stt.transcribe_file(audio_path, language)
    return result.text
```

### 3. Оновити config.yaml

```yaml
# ~/.config/atlastrinity/config.yaml

mcp:
  whisper:
    enabled: true
    model: "base"      # tiny, base, small, medium, large-v3
    language: "uk"
    download_root: "~/.config/atlastrinity/models/whisper"  # Опціонально
```

### 4. Оновити setup_dev.py

```python
# setup_dev.py

def ensure_directories():
    """Створює необхідні директорії"""
    dirs = [
        CONFIG_ROOT, 
        LOG_DIR, 
        MEMORY_DIR, 
        SCREENSHOTS_DIR, 
        MODELS_DIR,  # TTS
        CONFIG_ROOT / "models" / "whisper"  # ✅ Додати STT
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
```

---

## 📊 ПОРІВНЯННЯ ВАРІАНТІВ

| Критерій | Var 1 (~/.cache/) | Var 2 (config/) | Var 3 (symlink) |
|----------|-------------------|-----------------|-----------------|
| Консистентність | ❌ | ✅ | ✅ |
| Стандартність | ✅ | ❌ | ✅ |
| Складність | ✅ Easy | ⚠️ Medium | ⚠️ Medium |
| Сумісність | ✅ | ⚠️ | ✅ |
| Контроль | ❌ | ✅ | ✅ |

**РЕКОМЕНДАЦІЯ**: **Варіант 2** (перемістити в config/)
- Найпростіше
- Консистентно
- Повний контроль
- Змінити треба тільки 2 рядки коду

---

## ✅ ПЛАН ДІЙ

1. **Додати download_root в STT** ✅ Просто
2. **Інтегрувати config_loader в MCP Whisper** ✅ Просто
3. **Оновити setup_dev.py** ✅ Просто
4. **Протестувати завантаження моделі** ✅ Важливо
5. **Задокументувати** ✅ Обов'язково

---

## 🎯 ПОТОЧНА СТРУКТУРА (ПІСЛЯ ВИПРАВЛЕНЬ)

```
~/.config/atlastrinity/
├── .env
├── config.yaml
├── logs/
├── memory/
├── screenshots/
└── models/
    ├── tts/              ✅ TTS моделі
    │   ├── model.pth
    │   ├── config.yaml
    │   ├── feats_stats.npz
    │   └── spk_xvector.ark
    └── whisper/          ✅ STT моделі (після виправлень)
        ├── tiny.pt
        ├── base.pt
        ├── small.pt
        └── ...
```

---

## 📝 ВИСНОВОК

### ❌ Поточні проблеми:

1. Whisper моделі в `~/.cache/` замість `~/.config/atlastrinity/`
2. STT не використовує `download_root`
3. MCP Whisper не читає з `config.yaml`

### ✅ Рішення:

1. Додати `download_root` в `WhisperSTT.__init__()`
2. Інтегрувати `config_loader` в `whisper_server.py`
3. Створити `models/whisper/` в `setup_dev.py`
4. Протестувати завантаження моделі

### 🔧 Зміни (3 файли):

- `src/brain/voice/stt.py` - додати download_root
- `src/mcp/whisper_server.py` - config integration
- `setup_dev.py` - створити models/whisper/

**Складність**: Низька (10-15 хвилин)
**Пріоритет**: Високий (консистентність важлива)
