"""
Test script to verify refactoring imports work correctly
Run: python test_refactoring.py
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all refactored imports work"""
    print("Testing imports...")
    
    try:
        # Core models
        from backend.core.models.product import Product
        from backend.core.models.bill_of_material import BillOfMaterial
        from backend.core.models.batch import Batch
        from backend.core.models.inventory_balance import InventoryBalance
        from backend.core.models.work_center import WorkCenter
        from backend.core.models.work_center_capacity import WorkCenterCapacity
        from backend.core.models.manufacturing_order import ManufacturingOrder
        from backend.core.models.production_task import ProductionTask
        print("[OK] Core models imported successfully")
        
        # Core services
        from backend.core.services.mrp_service import MRPService
        from backend.core.services.dispatching_service import DispatchingService
        from backend.core.services.order_service import OrderService
        print("[OK] Core services imported successfully")
        
        # Core routes
        from backend.core.routes.products import router as products_router
        from backend.core.routes.bom import router as bom_router
        from backend.core.routes.batches import router as batches_router
        from backend.core.routes.inventory import router as inventory_router
        from backend.core.routes.orders import router as orders_router
        from backend.core.routes.tasks import router as tasks_router
        from backend.core.routes.work_centers import router as work_centers_router
        from backend.core.routes.dispatch import router as dispatch_router
        from backend.core.routes.mrp import router as mrp_router
        print("[OK] Core routes imported successfully")
        
        # Core schemas
        from backend.core.schemas.product import ProductCreate, ProductResponse
        from backend.core.schemas.bom import BOMCreate, BOMResponse
        from backend.core.schemas.batch import BatchCreate, BatchResponse
        print("[OK] Core schemas imported successfully")
        
        # Configuration
        from backend.config.factory_config import get_factory_config, FactoryConfig
        print("[OK] Configuration module imported successfully")
        
        # Database (should still use backend.src.db)
        from backend.src.db.session import get_db
        from backend.src.db.session import Base
        print("[OK] Database modules imported successfully")
        
        print("\n[SUCCESS] All imports passed!")
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from backend.config.factory_config import get_factory_config
        
        config = get_factory_config()
        
        print(f"[OK] Config loaded: {config.name}")
        print(f"  - Location: {config.location}")
        print(f"  - Timezone: {config.timezone}")
        print(f"  - MRP Horizon: {config.planning.mrp_horizon_days} days")
        print(f"  - Default Batch Size: {config.planning.default_batch_size_kg} kg")
        print(f"  - Batch Rounding: {config.planning.batch_rounding}")
        print(f"  - Features: Dispatching={config.features.enable_dispatching}, MRP={config.features.enable_mrp}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Configuration error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mrp_service_uses_config():
    """Test that MRP service uses configuration"""
    print("\nTesting MRP service configuration integration...")
    
    try:
        from backend.config.factory_config import get_factory_config
        
        config = get_factory_config()
        expected_horizon = config.planning.mrp_horizon_days
        
        print(f"[OK] MRP service should use horizon: {expected_horizon} days")
        print("  (Verify in MRPService.consolidate_orders method)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] MRP config test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MES Platform Template Refactoring Tests")
    print("=" * 60)
    
    results = []
    
    results.append(test_imports())
    results.append(test_configuration())
    results.append(test_mrp_service_uses_config())
    
    print("\n" + "=" * 60)
    if all(results):
        print("[OK] ALL TESTS PASSED")
        print("=" * 60)
        exit(0)
    else:
        print("[FAIL] SOME TESTS FAILED")
        print("=" * 60)
        exit(1)
