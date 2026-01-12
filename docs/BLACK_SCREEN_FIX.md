# Виправлення проблеми з чорним екраном (Black Screen Fix)

## Проблема

Коли Тетяна виконує альтернативний шлях (fallback) для виправлення ситуації, система використовує `osascript` команди для керування GUI macOS. Це викликає втрату фокусу Electron-додатку і призводить до чорного екрану.

## Симптоми

1. Тетяна каже: **"Виконую альтернативний крок для виправлення ситуації"**
2. Система виконує `osascript` команди для Cmd+V або інших дій
3. **Екран стає чорним** - рендерер зависає
4. Додаток не реагує на взаємодію

## Причина

### Ланцюг подій:

```
1. MCP fails → Tetyana uses fallback
2. Fallback calls osascript for keyboard simulation
3. osascript takes focus from Electron window
4. Electron renderer loses context
5. Black screen appears
```

### Проблемний код:

**До виправлення:**

```python
# src/brain/agents/tetyana.py:300
subprocess.run(["osascript", "-e", 
    'tell application "System Events" to key code 9 using {command down}'], 
    capture_output=True)
```

```python
# src/mcp/computer_use.py:42
subprocess.run(["osascript", "-e", 
    'tell application "System Events" to key code 9 using {command down}'])
```

## Виправлення

### 1. Захист на рівні MCP сервера

**Файл:** `src/mcp/computer_use.py`

```python
@server.tool()
def keyboard_paste(text: str) -> str:
    """Type text using clipboard (better for non-English)."""
    import subprocess
    import time
    try:
        # 🛡️ Save current frontmost app to restore focus
        get_app_script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = subprocess.run(["osascript", "-e", get_app_script], capture_output=True, text=True)
        frontmost_app = result.stdout.strip()
        
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
        time.sleep(0.1)
        
        # Cmd+V
        subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 9 using {command down}'])
        time.sleep(0.1)
        
        # 🛡️ Restore focus if it was an Electron app
        if frontmost_app and "Electron" in frontmost_app:
            restore_script = f'tell application "{frontmost_app}" to activate'
            subprocess.run(["osascript", "-e", restore_script], capture_output=True)
            
        return f"Pasted: {text}"
    except Exception as e:
        return f"Error pasting: {e}"
```

### 2. Захист у fallback коді агента

**Файл:** `src/brain/agents/tetyana.py`

Аналогічно додано збереження та відновлення фокусу в fallback-коді методу `_perform_gui_action`.

### 3. Захист на рівні Electron

**Файл:** `src/main/main.ts`

```typescript
// Protect against focus loss causing black screen
mainWindow.on('blur', () => {
    console.log('[ELECTRON] Window lost focus - monitoring for recovery');
    
    // Set timeout to restore focus if needed
    setTimeout(() => {
        if (mainWindow && !mainWindow.isFocused()) {
            console.log('[ELECTRON] Auto-restoring window focus');
            mainWindow.focus();
        }
    }, 500);
});

// Protect renderer from hanging
mainWindow.webContents.on('unresponsive', () => {
    console.error('[ELECTRON] Renderer became unresponsive - attempting reload');
    if (mainWindow) {
        mainWindow.webContents.reload();
    }
});

mainWindow.webContents.on('responsive', () => {
    console.log('[ELECTRON] Renderer became responsive again');
});
```

### 4. Додаткове логування

**Файл:** `src/brain/orchestrator.py`

```python
elif current_step == -1:
    # Alternative (recovery) step - different voice line
    await self._log("Starting alternative recovery step - monitoring for focus loss", "tetyana")
    await self._speak("tetyana", "Виконую альтернативний крок для виправлення ситуації.")
```

## Як працює виправлення

### Трирівневий захист:

1. **Python MCP рівень**: Зберігає поточний frontmost app перед виконанням osascript і відновлює його після
2. **Python Agent рівень**: Fallback код також зберігає/відновлює фокус
3. **Electron рівень**: Моніторить втрату фокусу і автоматично відновлює його через 500ms

### Моніторинг стану:

- Логування кожного кроку альтернативного шляху
- Відстеження unresponsive стану рендерера
- Автоматичне reload при зависанні

## Тестування

Після виправлення перевірте:

```bash
# 1. Перезапустіть всі процеси
pkill -f "npm run dev" && pkill -f "electron" && pkill -f "python.*server"

# 2. Запустіть додаток
npm run dev

# 3. Протестуйте сценарій, що викликав проблему
# Виконайте завдання, яке потребує fallback механізму
```

## Моніторинг

У консолі шукайте:

```
[ELECTRON] Window lost focus - monitoring for recovery
[ELECTRON] Auto-restoring window focus
[TETYANA] Starting alternative recovery step - monitoring for focus loss
```

Якщо бачите ці повідомлення - система працює коректно і захищає від втрати фокусу.

## Примітки

- Виправлення зворотньосумісне - не ламає існуючий функціонал
- Додає мінімальну затримку (0.1-0.2s) для стабільності
- Працює тільки на macOS (osascript специфічний для macOS)
- Захищає тільки Electron додатки (перевіряє "Electron" у назві процесу)

## Дата виправлення

6 січня 2026
