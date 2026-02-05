"""Question repository for database operations."""
from typing import List, Optional
from datetime import datetime
from ..models.entities import Question
from ..models.database import Database


class QuestionRepository:
    """Repository for managing question data."""

    def __init__(self, database: Database):
        """
        Initialize question repository.

        Args:
            database: Database instance
        """
        self.db = database

    def add(self, question: Question) -> Question:
        """
        Add a new question to the database.

        Args:
            question: Question entity to add

        Returns:
            Question: Added question with assigned ID
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO questions (content, answer, order_index)
                VALUES (?, ?, ?)
            """, (
                question.content,
                question.answer,
                question.order_index
            ))
            question.id = cursor.lastrowid
            return question

    def update(self, question: Question) -> Question:
        """
        Update an existing question.

        Args:
            question: Question entity with updated data

        Returns:
            Question: Updated question entity
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE questions
                SET content = ?, answer = ?, 
                    order_index = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                question.content,
                question.answer,
                question.order_index,
                question.id
            ))
            return question

    def delete(self, question_id: int) -> bool:
        """
        Delete a question by ID.

        Args:
            question_id: ID of question to delete

        Returns:
            bool: True if deleted, False otherwise
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            return cursor.rowcount > 0

    def get_by_id(self, question_id: int) -> Optional[Question]:
        """
        Get a question by ID.

        Args:
            question_id: ID of question to retrieve

        Returns:
            Question or None: Question entity if found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, content, answer, order_index, 
                       created_at, updated_at
                FROM questions WHERE id = ?
            """, (question_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_question(row)
            return None

    def get_all(self) -> List[Question]:
        """
        Get all questions.

        Returns:
            List[Question]: List of all questions
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, content, answer, order_index, 
                       created_at, updated_at
                FROM questions ORDER BY content
            """)
            return [self._row_to_question(row) for row in cursor.fetchall()]

    def search(self, keyword: str) -> List[Question]:
        """
        Search questions by keyword.

        Args:
            keyword: Search keyword

        Returns:
            List[Question]: List of matching questions
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, content, answer, order_index, 
                       created_at, updated_at
                FROM questions
                WHERE content LIKE ?
                ORDER BY content
            """, (f"%{keyword}%",))
            return [self._row_to_question(row) for row in cursor.fetchall()]

    def _row_to_question(self, row) -> Question:
        """
        Convert database row to Question entity.

        Args:
            row: Database row

        Returns:
            Question: Question entity
        """
        return Question(
            id=row['id'],
            content=row['content'],
            answer=row['answer'],
            order_index=row['order_index'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
