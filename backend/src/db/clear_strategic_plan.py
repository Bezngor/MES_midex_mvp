"""
Сброс плана стратегического планирования и резервов к начальному состоянию.

- Обнуляет reserved_quantity во всех записях inventory_balances.
- Удаляет все производственные задачи со статусом QUEUED (запланированные на Ганте).

Запуск из корня репозитория:
  python -m backend.src.db.clear_strategic_plan
"""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from backend.src.db.session import SessionLocal
from backend.core.services.strategic_planning_service import StrategicPlanningService


def main() -> None:
    db = SessionLocal()
    try:
        service = StrategicPlanningService(db)
        result = service.reset_plan_and_reservations()
        print(
            f"Сброс выполнен: удалено задач (QUEUED) — {result['tasks_deleted']}, "
            f"обнулено записей резервов — {result['reserves_cleared']}."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
    sys.exit(0)
