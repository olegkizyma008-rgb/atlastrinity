"""
AtlasTrinity Brain Package
"""

# Для уникнення помилок імпорту на етапі установки залежностей
# не імпортуємо важкі модулі на рівні пакета. Імпорт виконується пізніше при необхідності.
__all__ = []

try:
    from .agents import Atlas, Grisha, Tetyana
    from .orchestrator import Trinity

    __all__ = ["Trinity", "Atlas", "Tetyana", "Grisha"]
except Exception:
    # Залишаємо пакет мінімальним під час установки
    pass
