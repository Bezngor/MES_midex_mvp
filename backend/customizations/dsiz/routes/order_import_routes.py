"""
API routes для импорта заказов из CSV/Excel.
"""

from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.customizations.dsiz.services.order_import_service import OrderImportService
from backend.customizations.dsiz.schemas.order_import import ImportResult

router = APIRouter(prefix="/dsiz", tags=["DSIZ", "order-import"])


def get_order_import_service(db: Session = Depends(get_db)) -> OrderImportService:
    """Dependency для OrderImportService."""
    return OrderImportService(db)


EXCEL_MIMETYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}
CSV_MIMETYPES = {"text/csv", "text/plain", "application/csv"}


@router.post(
    "/orders/import",
    response_model=ImportResult,
    status_code=status.HTTP_200_OK,
    summary="Импорт заказов из CSV/Excel",
    description="Загрузка производственных заказов из .xlsx или .csv файла. "
    "Поддерживаемые колонки: order_number, customer, product_sku, quantity, due_date, priority.",
)
async def import_orders(
    file: UploadFile = File(..., description="Файл .xlsx или .csv"),
    db: Session = Depends(get_db),
    service: OrderImportService = Depends(get_order_import_service),
) -> ImportResult:
    """
    Импорт заказов покупателей из Excel или CSV.

    - **order_number** (обяз.): Уникальный номер заказа
    - **customer** (обяз.): Название клиента
    - **product_sku** (обяз.): SKU продукта (должен существовать в products.product_code)
    - **quantity** (обяз.): Количество (> 0)
    - **due_date** (обяз.): Дата выполнения (YYYY-MM-DD или DD.MM.YYYY)
    - **priority** (опц.): Срочно | Высокий | Обычный | Низкий (default: Обычный)

    Создаёт заказы с order_type=CUSTOMER, source_status=IMPORT и OrderSnapshot для отслеживания.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя файла не указано",
        )

    content_type = (file.content_type or "").strip().lower()
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл пустой",
        )

    filename_lower = file.filename.lower()

    if content_type in EXCEL_MIMETYPES or filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls"):
        return service.import_from_excel(file_bytes, file.filename or "upload.xlsx")
    if content_type in CSV_MIMETYPES or filename_lower.endswith(".csv"):
        return service.import_from_csv(file_bytes, file.filename or "upload.csv")

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Поддерживаемые форматы: .xlsx, .csv",
    )
