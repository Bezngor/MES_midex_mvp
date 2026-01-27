"""
Factory Configuration Loader
Loads factory-specific settings from YAML files
"""
import os
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field


class ShiftConfig(BaseModel):
    """Shift configuration"""
    enabled: bool = False
    config_file: Optional[str] = None


class PlanningConfig(BaseModel):
    """Production planning configuration"""
    mrp_horizon_days: int = 30
    batch_rounding: bool = True
    default_batch_size_kg: int = 1000


class InventoryConfig(BaseModel):
    """Inventory management configuration"""
    stock_buffer_days: int = 7
    reorder_point_enabled: bool = False
    fifo_enabled: bool = True


class WorkCenterConfig(BaseModel):
    """Work center configuration"""
    default_capacity_units_per_hour: int = 10
    parallel_capacity_enabled: bool = True


class QualityConfig(BaseModel):
    """Quality control configuration"""
    auto_qc_gates: bool = False
    inspection_required: bool = False


class IntegrationsConfig(BaseModel):
    """External integrations configuration"""
    n8n_webhook_url: Optional[str] = "http://localhost:5678/webhook"
    erp_api_url: Optional[str] = None
    wms_api_url: Optional[str] = None


class FeatureFlags(BaseModel):
    """Feature flags for enabling/disabling modules"""
    enable_dispatching: bool = True
    enable_gantt: bool = True
    enable_mrp: bool = True
    enable_batch_management: bool = True
    enable_quality_module: bool = False
    enable_genealogy: bool = True
    enable_serialization: bool = False


class FactoryConfig(BaseModel):
    """Factory configuration schema"""
    name: str = "Generic Manufacturing Facility"
    location: str = "Unknown"
    timezone: str = "UTC"
    shifts: ShiftConfig = Field(default_factory=ShiftConfig)
    planning: PlanningConfig = Field(default_factory=PlanningConfig)
    inventory: InventoryConfig = Field(default_factory=InventoryConfig)
    work_centers: WorkCenterConfig = Field(default_factory=WorkCenterConfig)
    quality: QualityConfig = Field(default_factory=QualityConfig)
    integrations: IntegrationsConfig = Field(default_factory=IntegrationsConfig)
    features: FeatureFlags = Field(default_factory=FeatureFlags)


class ConfigLoader:
    """Singleton configuration loader"""
    _instance: Optional['ConfigLoader'] = None
    _config: Optional[FactoryConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, config_path: Optional[str] = None) -> FactoryConfig:
        """Load factory configuration from YAML"""
        if self._config is not None:
            return self._config
        
        # Default path: check root config/ first, then backend/config/
        if config_path is None:
            root_config = Path("./config/factory_config.yaml")
            backend_config = Path("./backend/config/factory_config.yaml")
            if root_config.exists():
                config_path = str(root_config)
            elif backend_config.exists():
                config_path = str(backend_config)
            else:
                config_path = "./config/factory_config.yaml"  # Default fallback
            
        config_file = Path(config_path)
        
        # If custom config doesn't exist, use default
        if not config_file.exists():
            print(f"⚠️  Config file not found: {config_path}, using defaults")
            self._config = FactoryConfig()
            return self._config
            
        try:
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
                
            # Merge factory and features sections
            factory_data = data.get('factory', {})
            factory_data['features'] = data.get('features', {})
            
            self._config = FactoryConfig(**factory_data)
            print(f"✅ Loaded factory config: {self._config.name}")
            return self._config
            
        except Exception as e:
            print(f"❌ Error loading config: {e}, using defaults")
            self._config = FactoryConfig()
            return self._config
    
    @property
    def config(self) -> FactoryConfig:
        """Get loaded configuration"""
        if self._config is None:
            self.load()
        return self._config


# Global instance
_config_loader = ConfigLoader()


def get_factory_config() -> FactoryConfig:
    """Get factory configuration (singleton)"""
    return _config_loader.config
