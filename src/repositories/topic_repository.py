"""Topic repository for database operations."""
from typing import List, Optional
from datetime import datetime
from ..models.entities import Topic, Lesson
from ..models.database import Database


class TopicRepository:
    """Repository for managing topic data."""

    def __init__(self, database: Database):
        """
        Initialize topic repository.

        Args:
            database: Database instance
        """
        self.db = database

    def add(self, topic: Topic) -> Topic:
        """
        Add a new topic to the database.

        Args:
            topic: Topic entity to add

        Returns:
            Topic: Added topic with assigned ID
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO topics (title, description, order_index)
                VALUES (?, ?, ?)
            """, (
                topic.title,
                topic.description,
                topic.order_index
            ))
            topic.id = cursor.lastrowid
            return topic

    def update(self, topic: Topic) -> Topic:
        """
        Update an existing topic.

        Args:
            topic: Topic entity with updated data

        Returns:
            Topic: Updated topic entity
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE topics
                SET title = ?, description = ?, order_index = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                topic.title,
                topic.description,
                topic.order_index,
                topic.id
            ))
            return topic

    def delete(self, topic_id: int) -> bool:
        """
        Delete a topic by ID.

        Args:
            topic_id: ID of topic to delete

        Returns:
            bool: True if deleted, False otherwise
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
            return cursor.rowcount > 0

    def get_by_id(self, topic_id: int) -> Optional[Topic]:
        """
        Get a topic by ID.

        Args:
            topic_id: ID of topic to retrieve

        Returns:
            Topic or None: Topic entity if found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, order_index, 
                       created_at, updated_at
                FROM topics WHERE id = ?
            """, (topic_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_topic(row)
            return None

    def get_all(self) -> List[Topic]:
        """
        Get all topics.

        Returns:
            List[Topic]: List of all topics
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, order_index, 
                       created_at, updated_at
                FROM topics ORDER BY title
            """)
            return [self._row_to_topic(row) for row in cursor.fetchall()]

    def search(self, keyword: str) -> List[Topic]:
        """
        Search topics by keyword.

        Args:
            keyword: Search keyword

        Returns:
            List[Topic]: List of matching topics
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, order_index, 
                       created_at, updated_at
                FROM topics
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY title
            """, (f"%{keyword}%", f"%{keyword}%"))
            return [self._row_to_topic(row) for row in cursor.fetchall()]

    def add_lesson_to_topic(self, topic_id: int, lesson_id: int, order_index: int = 0) -> bool:
        """
        Add a lesson to a topic.

        Args:
            topic_id: ID of the topic
            lesson_id: ID of the lesson
            order_index: Order index for the lesson in the topic

        Returns:
            bool: True if added successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO topic_lessons (topic_id, lesson_id, order_index)
                    VALUES (?, ?, ?)
                """, (topic_id, lesson_id, order_index))
                return True
            except Exception:
                return False

    def remove_lesson_from_topic(self, topic_id: int, lesson_id: int) -> bool:
        """
        Remove a lesson from a topic.

        Args:
            topic_id: ID of the topic
            lesson_id: ID of the lesson

        Returns:
            bool: True if removed successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM topic_lessons 
                WHERE topic_id = ? AND lesson_id = ?
            """, (topic_id, lesson_id))
            return cursor.rowcount > 0

    def get_topic_lessons(self, topic_id: int) -> List[Lesson]:
        """
        Get all lessons for a specific topic.

        Args:
            topic_id: ID of the topic

        Returns:
            List[Lesson]: List of lessons in the topic
        """
        from .lesson_repository import LessonRepository

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id, l.title, l.description, l.duration_hours,
                       l.lesson_type_id, lt.name as lesson_type_name,
                       l.classroom_hours, l.self_study_hours,
                       l.order_index, l.created_at, l.updated_at
                FROM lessons l
                LEFT JOIN lesson_types lt ON l.lesson_type_id = lt.id
                JOIN topic_lessons tl ON l.id = tl.lesson_id
                WHERE tl.topic_id = ?
                ORDER BY tl.order_index
            """, (topic_id,))

            lesson_repo = LessonRepository(self.db)
            return [lesson_repo._row_to_lesson(row) for row in cursor.fetchall()]

    def get_topics_for_lesson(self, lesson_id: int) -> List[Topic]:
        """
        Get all topics that include a specific lesson.

        Args:
            lesson_id: ID of the lesson

        Returns:
            List[Topic]: Topics containing the lesson
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.title, t.description, t.order_index,
                       t.created_at, t.updated_at
                FROM topics t
                JOIN topic_lessons tl ON t.id = tl.topic_id
                WHERE tl.lesson_id = ?
                ORDER BY t.title
            """, (lesson_id,))
            return [self._row_to_topic(row) for row in cursor.fetchall()]

    def get_topics_for_question(self, question_id: int) -> List[Topic]:
        """
        Get all topics that include a specific question through lesson associations.

        Args:
            question_id: ID of the question

        Returns:
            List[Topic]: Topics containing the question
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT t.id, t.title, t.description, t.order_index,
                                t.created_at, t.updated_at
                FROM topics t
                JOIN topic_lessons tl ON t.id = tl.topic_id
                JOIN lesson_questions lq ON tl.lesson_id = lq.lesson_id
                WHERE lq.question_id = ?
                ORDER BY t.title
            """, (question_id,))
            return [self._row_to_topic(row) for row in cursor.fetchall()]

    def _row_to_topic(self, row) -> Topic:
        """
        Convert database row to Topic entity.

        Args:
            row: Database row

        Returns:
            Topic: Topic entity
        """
        return Topic(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            order_index=row['order_index'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
