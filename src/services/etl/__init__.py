"""ETL services module with data extraction, cleaning, transformation, and loading.

This module organizes ETL services into 4 functional domains:
- data_extraction: Fetching raw data from external sources
- data_cleaning: Normalizing and validating data formats
- data_transformation: Computing metrics and analytics
- data_loading: Persisting data to the database

For backward compatibility, all major classes can be imported directly
from this module, and submodules can be imported by their original paths.

Example:
    from services.etl import ExtractService, LoadService, TransformService
    from services.etl import metrics_calculator
    from services.etl.extract_service import ExtractService  # Also works
"""

import sys

# Import classes for direct access
from .data_extraction.extract_service import ExtractService
from .data_loading.load_service import LoadService
from .data_loading.pokemon_load_service import PokemonLoadService
from .data_loading.combat_load_service import CombatLoadService
from .data_cleaning.pokemon_cleaning_service import PokemonCleaningService
from .data_transformation.transform_service import TransformService
from .data_transformation.battle_metrics_service import BattleMetricsService

# Import submodules
from .data_transformation import metrics_calculator as _metrics_calculator
from .data_extraction import extract_service as _extract_service
from .data_loading import load_service as _load_service
from .data_loading import pokemon_load_service as _pokemon_load_service
from .data_loading import combat_load_service as _combat_load_service
from .data_cleaning import pokemon_cleaning_service as _pokemon_cleaning_service
from .data_transformation import battle_metrics_service as _battle_metrics_service
from .data_transformation import transform_service as _transform_service

# Register submodules in sys.modules for backward compatibility
# This allows: from services.etl.metrics_calculator import ...
_etl_base = "services.etl"
sys.modules[f"{_etl_base}.metrics_calculator"] = _metrics_calculator
sys.modules[f"{_etl_base}.extract_service"] = _extract_service
sys.modules[f"{_etl_base}.load_service"] = _load_service
sys.modules[f"{_etl_base}.pokemon_load_service"] = _pokemon_load_service
sys.modules[f"{_etl_base}.combat_load_service"] = _combat_load_service
sys.modules[f"{_etl_base}.pokemon_cleaning_service"] = _pokemon_cleaning_service
sys.modules[f"{_etl_base}.battle_metrics_service"] = _battle_metrics_service
sys.modules[f"{_etl_base}.transform_service"] = _transform_service

# Expose submodules at package level
metrics_calculator = _metrics_calculator

__all__ = [
    "ExtractService",
    "LoadService",
    "PokemonLoadService",
    "CombatLoadService",
    "PokemonCleaningService",
    "TransformService",
    "BattleMetricsService",
    "metrics_calculator",
]
