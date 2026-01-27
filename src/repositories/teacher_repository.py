"""Teacher repository for database operations."""
from typing import List, Optional
from datetime import datetime
from ..models.entities import Teacher
from ..models.database import Database


class TeacherRepository:
    """Repository for managing teacher data."""

    def __init__(self, database: Database):
        """
        Initialize teacher repository.

        Args:
            database: Database instance
        """
        self.db = database

    def add(self, teacher: Teacher) -> Teacher:
        """
        Add a new teacher to the database.

        Args:
            teacher: Teacher entity to add

        Returns:
            Teacher: Added teacher with assigned ID
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO teachers (full_name, position, department, email, phone)
                VALUES (?, ?, ?, ?, ?)
            """, (
                teacher.full_name,
                teacher.position,
                teacher.department,
                teacher.email,
                teacher.phone
            ))
            teacher.id = cursor.lastrowid
            return teacher

    def update(self, teacher: Teacher) -> Teacher:
        """
        Update an existing teacher.

        Args:
            teacher: Teacher entity with updated data

        Returns:
            Teacher: Updated teacher entity
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE teachers
                SET full_name = ?, position = ?, department = ?, 
                    email = ?, phone = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                teacher.full_name,
                teacher.position,
                teacher.department,
                teacher.email,
                teacher.phone,
                teacher.id
            ))
            return teacher

    def delete(self, teacher_id: int) -> bool:
        """
        Delete a teacher by ID.

        Args:
            teacher_id: ID of teacher to delete

        Returns:
            bool: True if deleted, False otherwise
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
            return cursor.rowcount > 0

    def get_by_id(self, teacher_id: int) -> Optional[Teacher]:
        """
        Get a teacher by ID.

        Args:
            teacher_id: ID of teacher to retrieve

        Returns:
            Teacher or None: Teacher entity if found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, full_name, position, department, email, phone, 
                       created_at, updated_at
                FROM teachers WHERE id = ?
            """, (teacher_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_teacher(row)
            return None

    def get_all(self) -> List[Teacher]:
        """
        Get all teachers.

        Returns:
            List[Teacher]: List of all teachers
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, full_name, position, department, email, phone, 
                       created_at, updated_at
                FROM teachers ORDER BY full_name
            """)
            return [self._row_to_teacher(row) for row in cursor.fetchall()]

    def search(self, keyword: str) -> List[Teacher]:
        """
        Search teachers by keyword.

        Args:
            keyword: Search keyword

        Returns:
            List[Teacher]: List of matching teachers
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, full_name, position, department, email, phone, 
                       created_at, updated_at
                FROM teachers
                WHERE full_name LIKE ? OR position LIKE ? OR department LIKE ?
                ORDER BY full_name
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            return [self._row_to_teacher(row) for row in cursor.fetchall()]

    def _row_to_teacher(self, row) -> Teacher:
        """
        Convert database row to Teacher entity.

        Args:
            row: Database row

        Returns:
            Teacher: Teacher entity
        """
        return Teacher(
            id=row['id'],
            full_name=row['full_name'],
            position=row['position'],
            department=row['department'],
            email=row['email'],
            phone=row['phone'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
