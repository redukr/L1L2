"""Migration runner helpers for Database."""

import sqlite3
from datetime import datetime

from ..services.app_paths import get_settings_dir


def ensure_schema_version(database, cursor) -> None:  # noqa: ANN001
    """Ensure schema migrations are applied in order."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER NOT NULL
        )
        """
    )
    cursor.execute("SELECT MAX(version) as version FROM schema_migrations")
    row = cursor.fetchone()
    current_version = row["version"] if row and row["version"] is not None else 1
    latest_version = database.SCHEMA_MIGRATIONS[-1][0]
    if current_version < latest_version:
        backup_database_before_migration(database, cursor.connection)
    for version, handler_name in database.SCHEMA_MIGRATIONS:
        if current_version >= version:
            continue
        getattr(database, handler_name)(cursor)
        cursor.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
        current_version = version


def backup_database_before_migration(database, conn) -> None:  # noqa: ANN001
    """Create a timestamped backup before running migrations on an existing DB."""
    if (
        database._migration_backup_created
        or not database._db_preexisting
        or not database.db_path
        or database.db_path == ":memory:"
    ):
        return
    backup_dir = get_settings_dir() / "schema_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"education_pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    with sqlite3.connect(str(backup_path)) as backup_conn:
        conn.backup(backup_conn)
    database._migration_backup_created = True
