"""Educational program repository for database operations."""
from typing import List, Optional
from datetime import datetime
from ..models.entities import EducationalProgram, Topic, Discipline
from ..models.database import Database


class ProgramRepository:
    """Repository for managing educational program data."""

    def __init__(self, database: Database):
        """
        Initialize program repository.

        Args:
            database: Database instance
        """
        self.db = database

    def add(self, program: EducationalProgram) -> EducationalProgram:
        """
        Add a new educational program to the database.

        Args:
            program: EducationalProgram entity to add

        Returns:
            EducationalProgram: Added program with assigned ID
        """
        if program.year is None:
            program.year = datetime.now().year
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO educational_programs (name, description, level, year, duration_hours)
                VALUES (?, ?, ?, ?, ?)
            """, (
                program.name,
                program.description,
                program.level,
                program.year,
                program.duration_hours
            ))
            program.id = cursor.lastrowid
            return program

    def update(self, program: EducationalProgram) -> EducationalProgram:
        """
        Update an existing educational program.

        Args:
            program: EducationalProgram entity with updated data

        Returns:
            EducationalProgram: Updated program entity
        """
        if program.year is None:
            program.year = datetime.now().year
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE educational_programs
                SET name = ?, description = ?, level = ?, year = ?,
                    duration_hours = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                program.name,
                program.description,
                program.level,
                program.year,
                program.duration_hours,
                program.id
            ))
            return program

    def delete(self, program_id: int) -> bool:
        """
        Delete an educational program by ID.

        Args:
            program_id: ID of program to delete

        Returns:
            bool: True if deleted, False otherwise
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM educational_programs WHERE id = ?", (program_id,))
            return cursor.rowcount > 0

    def get_by_id(self, program_id: int) -> Optional[EducationalProgram]:
        """
        Get an educational program by ID.

        Args:
            program_id: ID of program to retrieve

        Returns:
            EducationalProgram or None: Program entity if found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, level, year, duration_hours,
                       created_at, updated_at
                FROM educational_programs WHERE id = ?
            """, (program_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_program(row)
            return None

    def get_all(self) -> List[EducationalProgram]:
        """
        Get all educational programs.

        Returns:
            List[EducationalProgram]: List of all programs
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, level, year, duration_hours,
                       created_at, updated_at
                FROM educational_programs ORDER BY name
            """)
            return [self._row_to_program(row) for row in cursor.fetchall()]

    def search(self, keyword: str) -> List[EducationalProgram]:
        """
        Search educational programs by keyword.

        Args:
            keyword: Search keyword

        Returns:
            List[EducationalProgram]: List of matching programs
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, level, year, duration_hours,
                       created_at, updated_at
                FROM educational_programs
                WHERE name LIKE ? OR description LIKE ? OR level LIKE ?
                ORDER BY name
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            return [self._row_to_program(row) for row in cursor.fetchall()]

    def add_topic_to_program(self, program_id: int, topic_id: int, order_index: int = 0) -> bool:
        """
        Add a topic to an educational program.

        Args:
            program_id: ID of the program
            topic_id: ID of the topic
            order_index: Order index for the topic in the program

        Returns:
            bool: True if added successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO program_topics (program_id, topic_id, order_index)
                    VALUES (?, ?, ?)
                """, (program_id, topic_id, order_index))
                return True
            except Exception:
                return False

    def add_discipline_to_program(self, program_id: int, discipline_id: int, order_index: int = 0) -> bool:
        """
        Add a discipline to an educational program.

        Args:
            program_id: ID of the program
            discipline_id: ID of the discipline
            order_index: Order index for the discipline in the program

        Returns:
            bool: True if added successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO program_disciplines (program_id, discipline_id, order_index)
                    VALUES (?, ?, ?)
                """, (program_id, discipline_id, order_index))
                return True
            except Exception:
                return False

    def remove_topic_from_program(self, program_id: int, topic_id: int) -> bool:
        """
        Remove a topic from an educational program.

        Args:
            program_id: ID of the program
            topic_id: ID of the topic

        Returns:
            bool: True if removed successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM program_topics 
                WHERE program_id = ? AND topic_id = ?
            """, (program_id, topic_id))
            return cursor.rowcount > 0

    def remove_discipline_from_program(self, program_id: int, discipline_id: int) -> bool:
        """
        Remove a discipline from an educational program.

        Args:
            program_id: ID of the program
            discipline_id: ID of the discipline

        Returns:
            bool: True if removed successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM program_disciplines
                WHERE program_id = ? AND discipline_id = ?
            """, (program_id, discipline_id))
            return cursor.rowcount > 0

    def get_program_topics(self, program_id: int) -> List[Topic]:
        """
        Get all topics for a specific program.

        Args:
            program_id: ID of the program

        Returns:
            List[Topic]: List of topics in the program
        """
        from .topic_repository import TopicRepository

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.title, t.description, t.order_index, 
                       t.created_at, t.updated_at
                FROM topics t
                JOIN program_topics pt ON t.id = pt.topic_id
                WHERE pt.program_id = ?
                ORDER BY pt.order_index
            """, (program_id,))

            topic_repo = TopicRepository(self.db)
            return [topic_repo._row_to_topic(row) for row in cursor.fetchall()]

    def get_program_disciplines(self, program_id: int) -> List[Discipline]:
        """
        Get all disciplines for a specific program.

        Args:
            program_id: ID of the program

        Returns:
            List[Discipline]: List of disciplines in the program
        """
        from .discipline_repository import DisciplineRepository

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, d.name, d.description, pd.order_index as order_index,
                       d.created_at, d.updated_at
                FROM disciplines d
                JOIN program_disciplines pd ON d.id = pd.discipline_id
                WHERE pd.program_id = ?
                ORDER BY pd.order_index
            """, (program_id,))

            discipline_repo = DisciplineRepository(self.db)
            return [discipline_repo._row_to_discipline(row) for row in cursor.fetchall()]

    def get_programs_for_topic(self, topic_id: int) -> List[EducationalProgram]:
        """
        Get all programs that include a specific topic.

        Args:
            topic_id: ID of the topic

        Returns:
            List[EducationalProgram]: Programs containing the topic
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT p.id, p.name, p.description, p.level, p.year, p.duration_hours,
                                p.created_at, p.updated_at
                FROM educational_programs p
                JOIN program_disciplines pd ON p.id = pd.program_id
                JOIN discipline_topics dt ON pd.discipline_id = dt.discipline_id
                WHERE dt.topic_id = ?
                ORDER BY p.name
            """, (topic_id,))
            return [self._row_to_program(row) for row in cursor.fetchall()]

    def get_programs_for_discipline(self, discipline_id: int) -> List[EducationalProgram]:
        """
        Get all programs that include a specific discipline.

        Args:
            discipline_id: ID of the discipline

        Returns:
            List[EducationalProgram]: Programs containing the discipline
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.name, p.description, p.level, p.year, p.duration_hours,
                       p.created_at, p.updated_at
                FROM educational_programs p
                JOIN program_disciplines pd ON p.id = pd.program_id
                WHERE pd.discipline_id = ?
                ORDER BY p.name
            """, (discipline_id,))
            return [self._row_to_program(row) for row in cursor.fetchall()]

    def get_programs_for_lesson(self, lesson_id: int) -> List[EducationalProgram]:
        """
        Get all programs that include a specific lesson through topic associations.

        Args:
            lesson_id: ID of the lesson

        Returns:
            List[EducationalProgram]: Programs containing the lesson
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT p.id, p.name, p.description, p.level, p.year, p.duration_hours,
                                p.created_at, p.updated_at
                FROM educational_programs p
                JOIN program_disciplines pd ON p.id = pd.program_id
                JOIN discipline_topics dt ON pd.discipline_id = dt.discipline_id
                JOIN topic_lessons tl ON dt.topic_id = tl.topic_id
                WHERE tl.lesson_id = ?
                ORDER BY p.name
            """, (lesson_id,))
            return [self._row_to_program(row) for row in cursor.fetchall()]

    def get_programs_for_question(self, question_id: int) -> List[EducationalProgram]:
        """
        Get all programs that include a specific question through lesson associations.

        Args:
            question_id: ID of the question

        Returns:
            List[EducationalProgram]: Programs containing the question
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT p.id, p.name, p.description, p.level, p.year, p.duration_hours,
                                p.created_at, p.updated_at
                FROM educational_programs p
                JOIN program_disciplines pd ON p.id = pd.program_id
                JOIN discipline_topics dt ON pd.discipline_id = dt.discipline_id
                JOIN topic_lessons tl ON dt.topic_id = tl.topic_id
                JOIN lesson_questions lq ON tl.lesson_id = lq.lesson_id
                WHERE lq.question_id = ?
                ORDER BY p.name
            """, (question_id,))
            return [self._row_to_program(row) for row in cursor.fetchall()]

    def _row_to_program(self, row) -> EducationalProgram:
        """
        Convert database row to EducationalProgram entity.

        Args:
            row: Database row

        Returns:
            EducationalProgram: Program entity
        """
        return EducationalProgram(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            level=row['level'],
            year=row['year'] if 'year' in row.keys() else None,
            duration_hours=row['duration_hours'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
