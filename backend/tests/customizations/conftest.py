"""
Pytest configuration for customizations tests.

Переопределяет conftest из backend/tests/ для изоляции тестов кастомизаций.
Тесты кастомизаций могут требовать БД для тестирования сервисов.
"""

# Этот conftest переопределяет родительский conftest.py из backend/tests/
# но использует его фикстуры для БД

# Игнорируем родительский conftest, если он вызывает проблемы с импортами
import pytest
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для корректных импортов
# Это позволяет использовать импорты вида "from backend.customizations..."
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Импортируем фикстуру test_db из родительского conftest
# Это позволяет использовать БД в тестах кастомизаций
# Используем pytest_plugins для загрузки фикстур из родительского conftest
pytest_plugins = ["tests.conftest"]
