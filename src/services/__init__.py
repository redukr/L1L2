"""Services package for business logic layer."""
from .search_service import SearchService
from .auth_service import AuthService
from .demo_data import seed_demo_data
from .app_paths import get_app_base_dir, get_data_dir, get_materials_dir, get_translations_dir
from .i18n import I18nManager

__all__ = [
    "SearchService",
    "AuthService",
    "seed_demo_data",
    "get_app_base_dir",
    "get_data_dir",
    "get_materials_dir",
    "get_translations_dir",
    "I18nManager",
]
