"""Teacher repository for database operations."""
from typing import List, Optional
from datetime import datetime
from ..models.entities import Teacher, Discipline
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
                INSERT INTO teachers (full_name, military_rank, position, department, email, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                teacher.full_name,
                teacher.military_rank,
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
                SET full_name = ?, military_rank = ?, position = ?, department = ?, 
                    email = ?, phone = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                teacher.full_name,
                teacher.military_rank,
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
                SELECT id, full_name, military_rank, position, department, email, phone, 
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
                SELECT id, full_name, military_rank, position, department, email, phone, 
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
                SELECT id, full_name, military_rank, position, department, email, phone, 
                       created_at, updated_at
                FROM teachers
                WHERE full_name LIKE ? OR military_rank LIKE ? OR position LIKE ? OR department LIKE ? OR email LIKE ?
                ORDER BY full_name
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            return [self._row_to_teacher(row) for row in cursor.fetchall()]

    def add_discipline(self, teacher_id: int, discipline_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO teacher_disciplines (teacher_id, discipline_id)
                    VALUES (?, ?)
                """, (teacher_id, discipline_id))
                return True
            except Exception:
                return False

    def remove_discipline(self, teacher_id: int, discipline_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM teacher_disciplines
                WHERE teacher_id = ? AND discipline_id = ?
            """, (teacher_id, discipline_id))
            return cursor.rowcount > 0

    def get_disciplines(self, teacher_id: int) -> List[Discipline]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, d.name, d.description, d.order_index,
                       d.created_at, d.updated_at
                FROM disciplines d
                JOIN teacher_disciplines td ON d.id = td.discipline_id
                WHERE td.teacher_id = ?
                ORDER BY d.name
            """, (teacher_id,))
            return [self._row_to_discipline(row) for row in cursor.fetchall()]

    def get_teachers_for_disciplines(self, discipline_ids: List[int]) -> List[Teacher]:
        if not discipline_ids:
            return []
        placeholders = ",".join(["?"] * len(discipline_ids))
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT DISTINCT t.id, t.full_name, t.military_rank, t.position, t.department,
                                t.email, t.phone, t.created_at, t.updated_at
                FROM teachers t
                JOIN teacher_disciplines td ON t.id = td.teacher_id
                WHERE td.discipline_id IN ({placeholders})
                ORDER BY t.full_name
            """, discipline_ids)
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
            military_rank=row['military_rank'],
            position=row['position'],
            department=row['department'],
            email=row['email'],
            phone=row['phone'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

    def _row_to_discipline(self, row) -> Discipline:
        return Discipline(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            order_index=row["order_index"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )
