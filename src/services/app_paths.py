"""Application path helpers for dev and PyInstaller builds."""
from pathlib import Path
import sys


def get_app_base_dir() -> Path:
    """Return the directory where app data should be stored."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


def get_data_dir() -> Path:
    """Return the data directory, creating it if needed."""
    data_dir = get_app_base_dir() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_materials_dir() -> Path:
    """Return the materials directory, creating it if needed."""
    materials_dir = get_data_dir() / "materials"
    materials_dir.mkdir(exist_ok=True)
    return materials_dir
