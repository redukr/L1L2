"""Application path helpers for dev and PyInstaller builds."""
from pathlib import Path
import sys


def get_app_base_dir() -> Path:
    """Return the directory where app data should be stored."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


def make_relative_to_app(path: Path | str) -> str:
    """Return a path relative to app base dir when possible."""
    base = get_app_base_dir().resolve()
    target = Path(path).resolve()
    try:
        return str(target.relative_to(base))
    except ValueError:
        return str(target)


def resolve_app_path(path: Path | str) -> Path:
    """Resolve a possibly-relative path under app base dir."""
    if not path:
        return Path("")
    p = Path(path)
    if p.is_absolute():
        return p
    return (get_app_base_dir() / p).resolve()


def get_resource_base_dir() -> Path:
    """Return the directory for bundled resources."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", get_app_base_dir()))
    return Path(__file__).resolve().parent.parent.parent


def get_data_dir() -> Path:
    """Return the data directory, creating it if needed."""
    data_dir = get_app_base_dir() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_database_dir() -> Path:
    """Return the database directory, creating it if needed."""
    database_dir = get_app_base_dir() / "database"
    database_dir.mkdir(exist_ok=True)
    return database_dir


def get_files_dir() -> Path:
    """Return the file storage directory, creating it if needed."""
    files_dir = get_app_base_dir() / "files"
    files_dir.mkdir(exist_ok=True)
    return files_dir


def get_settings_dir() -> Path:
    """Return the settings directory, creating it if needed."""
    settings_dir = get_app_base_dir() / "settings"
    settings_dir.mkdir(exist_ok=True)
    return settings_dir


def get_materials_dir() -> Path:
    """Return the materials directory, creating it if needed."""
    materials_dir = get_files_dir() / "materials"
    materials_dir.mkdir(exist_ok=True)
    return materials_dir


def get_translations_dir() -> Path:
    """Return the directory that stores translation files."""
    return get_resource_base_dir() / "translations"
