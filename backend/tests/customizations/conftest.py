"""
Pytest configuration for customizations tests.

Переопределяет conftest из backend/tests/ для изоляции тестов кастомизаций.
Тесты кастомизаций не требуют БД и могут работать изолированно.
"""

# Этот conftest переопределяет родительский conftest.py из backend/tests/
# чтобы тесты кастомизаций могли работать без БД-зависимостей

# Игнорируем родительский conftest, если он вызывает проблемы с импортами
import pytest
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для корректных импортов
# Это позволяет использовать импорты вида "from backend.customizations..."
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Можно добавить фикстуры для кастомизаций здесь, если понадобится
