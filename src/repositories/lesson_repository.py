"""Lesson repository for database operations."""
from typing import List, Optional
from datetime import datetime
from ..models.entities import Lesson, Question
from ..models.database import Database


class LessonRepository:
    """Repository for managing lesson data."""

    def __init__(self, database: Database):
        """
        Initialize lesson repository.

        Args:
            database: Database instance
        """
        self.db = database

    def add(self, lesson: Lesson) -> Lesson:
        """
        Add a new lesson to the database.

        Args:
            lesson: Lesson entity to add

        Returns:
            Lesson: Added lesson with assigned ID
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lessons (
                    title, description, duration_hours, lesson_type_id,
                    classroom_hours, self_study_hours, order_index
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                lesson.title,
                lesson.description,
                lesson.duration_hours,
                lesson.lesson_type_id,
                lesson.classroom_hours,
                lesson.self_study_hours,
                lesson.order_index
            ))
            lesson.id = cursor.lastrowid
            return lesson

    def update(self, lesson: Lesson) -> Lesson:
        """
        Update an existing lesson.

        Args:
            lesson: Lesson entity with updated data

        Returns:
            Lesson: Updated lesson entity
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lessons
                SET title = ?, description = ?, duration_hours = ?,
                    lesson_type_id = ?, classroom_hours = ?, self_study_hours = ?,
                    order_index = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                lesson.title,
                lesson.description,
                lesson.duration_hours,
                lesson.lesson_type_id,
                lesson.classroom_hours,
                lesson.self_study_hours,
                lesson.order_index,
                lesson.id
            ))
            return lesson

    def delete(self, lesson_id: int) -> bool:
        """
        Delete a lesson by ID.

        Args:
            lesson_id: ID of lesson to delete

        Returns:
            bool: True if deleted, False otherwise
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
            return cursor.rowcount > 0

    def get_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """
        Get a lesson by ID.

        Args:
            lesson_id: ID of lesson to retrieve

        Returns:
            Lesson or None: Lesson entity if found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id, l.title, l.description, l.duration_hours,
                       l.lesson_type_id, lt.name as lesson_type_name,
                       l.classroom_hours, l.self_study_hours,
                       l.order_index, l.created_at, l.updated_at
                FROM lessons l
                LEFT JOIN lesson_types lt ON l.lesson_type_id = lt.id
                WHERE l.id = ?
            """, (lesson_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_lesson(row)
            return None

    def get_all(self) -> List[Lesson]:
        """
        Get all lessons.

        Returns:
            List[Lesson]: List of all lessons
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id, l.title, l.description, l.duration_hours,
                       l.lesson_type_id, lt.name as lesson_type_name,
                       l.classroom_hours, l.self_study_hours,
                       l.order_index, l.created_at, l.updated_at
                FROM lessons l
                LEFT JOIN lesson_types lt ON l.lesson_type_id = lt.id
                ORDER BY l.title
            """)
            return [self._row_to_lesson(row) for row in cursor.fetchall()]

    def search(self, keyword: str) -> List[Lesson]:
        """
        Search lessons by keyword.

        Args:
            keyword: Search keyword

        Returns:
            List[Lesson]: List of matching lessons
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id, l.title, l.description, l.duration_hours,
                       l.lesson_type_id, lt.name as lesson_type_name,
                       l.classroom_hours, l.self_study_hours,
                       l.order_index, l.created_at, l.updated_at
                FROM lessons l
                LEFT JOIN lesson_types lt ON l.lesson_type_id = lt.id
                WHERE l.title LIKE ? OR l.description LIKE ?
                ORDER BY l.title
            """, (f"%{keyword}%", f"%{keyword}%"))
            return [self._row_to_lesson(row) for row in cursor.fetchall()]

    def add_question_to_lesson(self, lesson_id: int, question_id: int, order_index: int = 0) -> bool:
        """
        Add a question to a lesson.

        Args:
            lesson_id: ID of the lesson
            question_id: ID of the question
            order_index: Order index for the question in the lesson

        Returns:
            bool: True if added successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO lesson_questions (lesson_id, question_id, order_index)
                    VALUES (?, ?, ?)
                """, (lesson_id, question_id, order_index))
                return True
            except Exception:
                return False

    def update_question_order(self, lesson_id: int, question_id: int, order_index: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lesson_questions
                SET order_index = ?
                WHERE lesson_id = ? AND question_id = ?
            """, (order_index, lesson_id, question_id))
            return cursor.rowcount > 0

    def get_next_question_order(self, lesson_id: int) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(MAX(order_index), 0) + 1 as next_idx
                FROM lesson_questions
                WHERE lesson_id = ?
            """, (lesson_id,))
            row = cursor.fetchone()
            return row["next_idx"] if row else 1

    def remove_question_from_lesson(self, lesson_id: int, question_id: int) -> bool:
        """
        Remove a question from a lesson.

        Args:
            lesson_id: ID of the lesson
            question_id: ID of the question

        Returns:
            bool: True if removed successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM lesson_questions 
                WHERE lesson_id = ? AND question_id = ?
            """, (lesson_id, question_id))
            return cursor.rowcount > 0

    def get_lesson_questions(self, lesson_id: int) -> List[Question]:
        """
        Get all questions for a specific lesson.

        Args:
            lesson_id: ID of the lesson

        Returns:
            List[Question]: List of questions in the lesson
        """
        from .question_repository import QuestionRepository

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.id, q.content, q.answer, q.difficulty_level, 
                       q.order_index, q.created_at, q.updated_at
                FROM questions q
                JOIN lesson_questions lq ON q.id = lq.question_id
                WHERE lq.lesson_id = ?
                ORDER BY CASE
                    WHEN lq.order_index IS NULL OR lq.order_index = 0 THEN q.order_index
                    ELSE lq.order_index
                END, q.order_index
            """, (lesson_id,))

            question_repo = QuestionRepository(self.db)
            return [question_repo._row_to_question(row) for row in cursor.fetchall()]

    def normalize_question_order(self, lesson_id: int) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lq.question_id,
                       CASE
                           WHEN q.order_index IS NULL OR q.order_index = 0 THEN (1000000 + lq.rowid)
                           ELSE q.order_index
                       END as sort_key
                FROM lesson_questions lq
                JOIN questions q ON q.id = lq.question_id
                WHERE lq.lesson_id = ?
                ORDER BY sort_key
            """, (lesson_id,))
            rows = cursor.fetchall()
            for idx, row in enumerate(rows, start=1):
                cursor.execute("""
                    UPDATE lesson_questions
                    SET order_index = ?
                    WHERE lesson_id = ? AND question_id = ?
                """, (idx, lesson_id, row["question_id"]))

    def get_lessons_for_question(self, question_id: int) -> List[Lesson]:
        """
        Get all lessons that include a specific question.

        Args:
            question_id: ID of the question

        Returns:
            List[Lesson]: Lessons containing the question
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id, l.title, l.description, l.duration_hours,
                       l.lesson_type_id, lt.name as lesson_type_name,
                       l.classroom_hours, l.self_study_hours,
                       l.order_index, l.created_at, l.updated_at
                FROM lessons l
                LEFT JOIN lesson_types lt ON l.lesson_type_id = lt.id
                JOIN lesson_questions lq ON l.id = lq.lesson_id
                WHERE lq.question_id = ?
                ORDER BY l.title
            """, (question_id,))
            return [self._row_to_lesson(row) for row in cursor.fetchall()]

    def _row_to_lesson(self, row) -> Lesson:
        """
        Convert database row to Lesson entity.

        Args:
            row: Database row

        Returns:
            Lesson: Lesson entity
        """
        return Lesson(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            duration_hours=row['duration_hours'],
            lesson_type_id=row['lesson_type_id'],
            lesson_type_name=row['lesson_type_name'],
            classroom_hours=row['classroom_hours'],
            self_study_hours=row['self_study_hours'],
            order_index=row['order_index'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
