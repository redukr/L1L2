"""Material type repository for database operations."""
from typing import List, Optional
from ..models.database import Database
from ..models.entities import MaterialType


class MaterialTypeRepository:
    """Repository for managing material types."""

    def __init__(self, database: Database):
        self.db = database

    def get_all(self) -> List[MaterialType]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, created_at, updated_at
                FROM material_types
                ORDER BY name
            """)
            return [self._row_to_type(row) for row in cursor.fetchall()]

    def add(self, material_type: MaterialType) -> MaterialType:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO material_types (name) VALUES (?)",
                (material_type.name,),
            )
            material_type.id = cursor.lastrowid
            return material_type

    def update(self, material_type: MaterialType) -> MaterialType:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE material_types
                SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (material_type.name, material_type.id),
            )
            return material_type

    def delete(self, material_type_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM material_types WHERE id = ?", (material_type_id,))
            return cursor.rowcount > 0

    def _row_to_type(self, row) -> MaterialType:  # noqa: ANN001
        return MaterialType(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
