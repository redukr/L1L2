"""Bootstrap helpers for the SQLite schema."""

from .schema import CORE_TABLE_STATEMENTS, FTS_TABLE_STATEMENTS, INDEX_STATEMENTS


def initialize_database(database, conn) -> None:  # noqa: ANN001
    """Create core schema, indexes, FTS tables, triggers, and seed defaults."""
    cursor = conn.cursor()

    for statement in CORE_TABLE_STATEMENTS:
        cursor.execute(statement)

    for statement in INDEX_STATEMENTS:
        cursor.execute(statement)

    for statement in FTS_TABLE_STATEMENTS:
        cursor.execute(statement)

    database._create_fts_triggers(cursor)
    database._ensure_schema_version(cursor)
    database._ensure_default_lesson_types(cursor)
