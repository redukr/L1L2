"""Methodical material repository for database operations."""
from typing import List, Optional, Tuple
from datetime import datetime
from ..models.entities import MethodicalMaterial, Teacher
from ..models.database import Database


class MaterialRepository:
    """Repository for managing methodical material data."""

    def __init__(self, database: Database):
        """
        Initialize material repository.

        Args:
            database: Database instance
        """
        self.db = database

    def add(self, material: MethodicalMaterial) -> MethodicalMaterial:
        """
        Add a new methodical material to the database.

        Args:
            material: MethodicalMaterial entity to add

        Returns:
            MethodicalMaterial: Added material with assigned ID
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO methodical_materials 
                (title, material_type, description, original_filename, stored_filename,
                 relative_path, file_type, file_path, file_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                material.title,
                material.material_type,
                material.description,
                material.original_filename,
                material.stored_filename,
                material.relative_path,
                material.file_type,
                material.file_path,
                material.file_name
            ))
            material.id = cursor.lastrowid
            return material

    def update(self, material: MethodicalMaterial) -> MethodicalMaterial:
        """
        Update an existing methodical material.

        Args:
            material: MethodicalMaterial entity with updated data

        Returns:
            MethodicalMaterial: Updated material entity
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE methodical_materials
                SET title = ?, material_type = ?, description = ?, 
                    original_filename = ?, stored_filename = ?, relative_path = ?, file_type = ?,
                    file_path = ?, file_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                material.title,
                material.material_type,
                material.description,
                material.original_filename,
                material.stored_filename,
                material.relative_path,
                material.file_type,
                material.file_path,
                material.file_name,
                material.id
            ))
            return material

    def delete(self, material_id: int) -> bool:
        """
        Delete a methodical material by ID.

        Args:
            material_id: ID of material to delete

        Returns:
            bool: True if deleted, False otherwise
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM methodical_materials WHERE id = ?", (material_id,))
            return cursor.rowcount > 0

    def get_by_id(self, material_id: int) -> Optional[MethodicalMaterial]:
        """
        Get a methodical material by ID.

        Args:
            material_id: ID of material to retrieve

        Returns:
            MethodicalMaterial or None: Material entity if found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, material_type, description,
                       original_filename, stored_filename, relative_path, file_type,
                       file_path, file_name, created_at, updated_at
                FROM methodical_materials WHERE id = ?
            """, (material_id,))
            row = cursor.fetchone()

            if row:
                material = self._row_to_material(row)
                # Load associated teachers
                material.teachers = self.get_material_teachers(material_id)
                return material
            return None

    def get_all(self) -> List[MethodicalMaterial]:
        """
        Get all methodical materials.

        Returns:
            List[MethodicalMaterial]: List of all materials
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, material_type, description,
                       original_filename, stored_filename, relative_path, file_type,
                       file_path, file_name, created_at, updated_at
                FROM methodical_materials ORDER BY title
            """)
            materials = []
            for row in cursor.fetchall():
                material = self._row_to_material(row)
                material.teachers = self.get_material_teachers(material.id)
                materials.append(material)
            return materials

    def search(self, keyword: str) -> List[MethodicalMaterial]:
        """
        Search methodical materials by keyword.

        Args:
            keyword: Search keyword

        Returns:
            List[MethodicalMaterial]: List of matching materials
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, material_type, description,
                       original_filename, stored_filename, relative_path, file_type,
                       file_path, file_name, created_at, updated_at
                FROM methodical_materials
                WHERE title LIKE ? OR description LIKE ? OR file_name LIKE ? OR original_filename LIKE ?
                ORDER BY title
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            materials = []
            for row in cursor.fetchall():
                material = self._row_to_material(row)
                material.teachers = self.get_material_teachers(material.id)
                materials.append(material)
            return materials

    def get_materials_for_entity(self, entity_type: str, entity_id: int) -> List[MethodicalMaterial]:
        """
        Get all materials associated with a specific entity.

        Args:
            entity_type: Type of entity ('program', 'topic', or 'lesson')
            entity_id: ID of the entity

        Returns:
            List[MethodicalMaterial]: List of materials for the entity
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.id, m.title, m.material_type, m.description,
                       m.original_filename, m.stored_filename, m.relative_path, m.file_type,
                       m.file_path, m.file_name, m.created_at, m.updated_at
                FROM methodical_materials m
                JOIN material_associations ma ON m.id = ma.material_id
                WHERE ma.entity_type = ? AND ma.entity_id = ?
                ORDER BY m.title
            """, (entity_type, entity_id))

            materials = []
            for row in cursor.fetchall():
                material = self._row_to_material(row)
                material.teachers = self.get_material_teachers(material.id)
                materials.append(material)
            return materials

    def add_material_to_entity(self, material_id: int, entity_type: str, entity_id: int) -> bool:
        """
        Associate a material with an entity.

        Args:
            material_id: ID of the material
            entity_type: Type of entity ('program', 'topic', or 'lesson')
            entity_id: ID of the entity

        Returns:
            bool: True if added successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO material_associations (material_id, entity_type, entity_id)
                    VALUES (?, ?, ?)
                """, (material_id, entity_type, entity_id))
                return True
            except Exception:
                return False

    def remove_material_from_entity(self, material_id: int, entity_type: str, entity_id: int) -> bool:
        """
        Remove a material association from an entity.

        Args:
            material_id: ID of the material
            entity_type: Type of entity ('program', 'topic', or 'lesson')
            entity_id: ID of the entity

        Returns:
            bool: True if removed successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM material_associations 
                WHERE material_id = ? AND entity_type = ? AND entity_id = ?
            """, (material_id, entity_type, entity_id))
            return cursor.rowcount > 0

    def add_teacher_to_material(self, teacher_id: int, material_id: int, role: str = 'author') -> bool:
        """
        Associate a teacher with a material.

        Args:
            teacher_id: ID of the teacher
            material_id: ID of the material
            role: Role of the teacher (default: 'author')

        Returns:
            bool: True if added successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO teacher_materials (teacher_id, material_id, role)
                    VALUES (?, ?, ?)
                """, (teacher_id, material_id, role))
                return True
            except Exception:
                return False

    def remove_teacher_from_material(self, teacher_id: int, material_id: int) -> bool:
        """
        Remove a teacher association from a material.

        Args:
            teacher_id: ID of the teacher
            material_id: ID of the material

        Returns:
            bool: True if removed successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM teacher_materials 
                WHERE teacher_id = ? AND material_id = ?
            """, (teacher_id, material_id))
            return cursor.rowcount > 0

    def get_material_associations(self, material_id: int) -> List[Tuple[str, int]]:
        """
        Get all entity associations for a material.

        Args:
            material_id: ID of the material

        Returns:
            List[Tuple[str, int]]: List of (entity_type, entity_id)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT entity_type, entity_id
                FROM material_associations
                WHERE material_id = ?
                ORDER BY entity_type, entity_id
            """, (material_id,))
            return [(row['entity_type'], row['entity_id']) for row in cursor.fetchall()]

    def get_material_association_labels(self, material_id: int) -> List[Tuple[str, int, str]]:
        """
        Get all entity associations for a material with display titles.

        Args:
            material_id: ID of the material

        Returns:
            List[Tuple[str, int, str]]: (entity_type, entity_id, title)
        """
        associations = self.get_material_associations(material_id)
        labeled = []
        for entity_type, entity_id in associations:
            title = self._resolve_entity_title(entity_type, entity_id)
            labeled.append((entity_type, entity_id, title))
        return labeled

    def _resolve_entity_title(self, entity_type: str, entity_id: int) -> str:
        """Resolve a human-readable title for an entity."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if entity_type == 'program':
                cursor.execute("SELECT name FROM educational_programs WHERE id = ?", (entity_id,))
                row = cursor.fetchone()
                return row['name'] if row else f"Program #{entity_id}"
            if entity_type == 'discipline':
                cursor.execute("SELECT name FROM disciplines WHERE id = ?", (entity_id,))
                row = cursor.fetchone()
                return row['name'] if row else f"Discipline #{entity_id}"
            if entity_type == 'topic':
                cursor.execute("SELECT title FROM topics WHERE id = ?", (entity_id,))
                row = cursor.fetchone()
                return row['title'] if row else f"Topic #{entity_id}"
            if entity_type == 'lesson':
                cursor.execute("SELECT title FROM lessons WHERE id = ?", (entity_id,))
                row = cursor.fetchone()
                return row['title'] if row else f"Lesson #{entity_id}"
        return f"{entity_type} #{entity_id}"

    def get_material_teachers(self, material_id: int) -> List[Teacher]:
        """
        Get all teachers associated with a material.

        Args:
            material_id: ID of the material

        Returns:
            List[Teacher]: List of teachers associated with the material
        """
        from .teacher_repository import TeacherRepository

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.full_name, t.military_rank, t.position, t.department, 
                       t.email, t.phone, t.created_at, t.updated_at
                FROM teachers t
                JOIN teacher_materials tm ON t.id = tm.teacher_id
                WHERE tm.material_id = ?
                ORDER BY t.full_name
            """, (material_id,))

            teacher_repo = TeacherRepository(self.db)
            return [teacher_repo._row_to_teacher(row) for row in cursor.fetchall()]

    def _row_to_material(self, row) -> MethodicalMaterial:
        """
        Convert database row to MethodicalMaterial entity.

        Args:
            row: Database row

        Returns:
            MethodicalMaterial: Material entity
        """
        return MethodicalMaterial(
            id=row['id'],
            title=row['title'],
            material_type=row['material_type'],
            description=row['description'],
            original_filename=row['original_filename'],
            stored_filename=row['stored_filename'],
            relative_path=row['relative_path'],
            file_type=row['file_type'],
            file_path=row['file_path'],
            file_name=row['file_name'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
