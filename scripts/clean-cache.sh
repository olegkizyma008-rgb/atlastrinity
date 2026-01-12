#!/bin/bash

# Скрипт для повного очищення кешу перед запуском dev режиму

echo "🧹 Очищення всіх кешів..."

# Очищення Python кешу
echo "  • Очищення Python __pycache__..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Очищення Node кешу
echo "  • Очищення Node node_modules/.cache..."
rm -rf node_modules/.cache 2>/dev/null

# Очищення Vite кешу
echo "  • Очищення Vite кешу..."
rm -rf .vite 2>/dev/null

# Очищення Electron cache
echo "  • Очищення Electron кешу..."
rm -rf ~/Library/Caches/atlastrinity* 2>/dev/null

# Очищення зображень STT/TTT
echo "  • Очищення тимчасових файлів..."
rm -rf ~/.config/atlastrinity/screenshots/*.png 2>/dev/null

echo "✅ Кеші очищені!"
