"""Search service for full-text search across all entities."""
from typing import List, Dict, Any
import sqlite3
from ..models.entities import SearchResult
from ..models.database import Database
from ..repositories.teacher_repository import TeacherRepository
from ..repositories.program_repository import ProgramRepository
from ..repositories.discipline_repository import DisciplineRepository
from ..repositories.topic_repository import TopicRepository
from ..repositories.lesson_repository import LessonRepository
from ..repositories.question_repository import QuestionRepository
from ..repositories.material_repository import MaterialRepository


class SearchService:
    """Service for performing full-text searches across all entities."""

    def __init__(self, database: Database):
        """
        Initialize search service.

        Args:
            database: Database instance
        """
        self.db = database
        self.teacher_repo = TeacherRepository(database)
        self.program_repo = ProgramRepository(database)
        self.discipline_repo = DisciplineRepository(database)
        self.topic_repo = TopicRepository(database)
        self.lesson_repo = LessonRepository(database)
        self.question_repo = QuestionRepository(database)
        self.material_repo = MaterialRepository(database)

    def _fts_query(self, keyword: str) -> str:
        tokens = [t for t in keyword.strip().split() if t]
        if not tokens:
            return keyword
        return " ".join(f"{token}*" for token in tokens)

    def search_all(self, keyword: str) -> List[SearchResult]:
        """
        Perform full-text search across all entities.

        Args:
            keyword: Search keyword or phrase

        Returns:
            List[SearchResult]: List of search results with relevance scores
        """
        if not keyword or not keyword.strip():
            return []

        results = []

        # Search in teachers
        results.extend(self._search_teachers(keyword))

        # Search in educational programs
        results.extend(self._search_programs(keyword))

        # Search in disciplines
        results.extend(self._search_disciplines(keyword))

        # Search in topics
        results.extend(self._search_topics(keyword))

        # Search in lessons
        results.extend(self._search_lessons(keyword))

        # Search in questions
        results.extend(self._search_questions(keyword))

        # Search in methodical materials
        results.extend(self._search_materials(keyword))

        # Sort results by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results

    def _search_teachers(self, keyword: str) -> List[SearchResult]:
        """Search in teachers using FTS."""
        results: List[SearchResult] = []
        fts_query = self._fts_query(keyword)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT t.id, t.full_name, t.military_rank, t.position, t.department,
                           t.email, t.phone, bm25(teachers_fts) as score
                    FROM teachers t
                    JOIN teachers_fts ON t.id = teachers_fts.rowid
                    WHERE teachers_fts MATCH ?
                    ORDER BY score
                """, (fts_query,))

                for row in cursor.fetchall():
                    matched_text = self._get_matched_text(
                        row, ['full_name', 'military_rank', 'position', 'department', 'email', 'phone']
                    )
                    description = f"{row['position'] or ''} - {row['department'] or ''}"
                    results.append(SearchResult(
                        entity_type='teacher',
                        entity_id=row['id'],
                        title=row['full_name'],
                        description=description.strip(' -'),
                        matched_text=matched_text,
                        relevance_score=-(row['score'] or 0)
                    ))
            except sqlite3.Error:
                results = []

        return results or self._fallback_teachers(keyword)

    def _search_programs(self, keyword: str) -> List[SearchResult]:
        """Search in educational programs using FTS."""
        results = []
        fts_query = self._fts_query(keyword)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT p.id, p.name, p.description, p.level, 
                           p.duration_hours, bm25(programs_fts) as score
                    FROM educational_programs p
                    JOIN programs_fts ON p.id = programs_fts.rowid
                    WHERE programs_fts MATCH ?
                    ORDER BY score
                """, (fts_query,))

                for row in cursor.fetchall():
                    matched_text = self._get_matched_text(
                        row, ['name', 'description', 'level']
                    )
                    description = f"{row['level'] or ''} - {row['description'] or ''}"
                    results.append(SearchResult(
                        entity_type='program',
                        entity_id=row['id'],
                        title=row['name'],
                        description=description.strip(' -'),
                        matched_text=matched_text,
                        relevance_score=-(row['score'] or 0)
                    ))
            except sqlite3.Error:
                results = []

        return results or self._fallback_programs(keyword)

    def _search_disciplines(self, keyword: str) -> List[SearchResult]:
        """Search in disciplines using FTS."""
        results = []
        fts_query = self._fts_query(keyword)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT d.id, d.name, d.description, bm25(disciplines_fts) as score
                    FROM disciplines d
                    JOIN disciplines_fts ON d.id = disciplines_fts.rowid
                    WHERE disciplines_fts MATCH ?
                    ORDER BY score
                """, (fts_query,))

                for row in cursor.fetchall():
                    matched_text = self._get_matched_text(
                        row, ['name', 'description']
                    )
                    results.append(SearchResult(
                        entity_type='discipline',
                        entity_id=row['id'],
                        title=row['name'],
                        description=row['description'] or '',
                        matched_text=matched_text,
                        relevance_score=-(row['score'] or 0)
                    ))
            except sqlite3.Error:
                results = []

        return results or self._fallback_disciplines(keyword)

    def _search_topics(self, keyword: str) -> List[SearchResult]:
        """Search in topics using FTS."""
        results = []
        fts_query = self._fts_query(keyword)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT t.id, t.title, t.description, bm25(topics_fts) as score
                    FROM topics t
                    JOIN topics_fts ON t.id = topics_fts.rowid
                    WHERE topics_fts MATCH ?
                    ORDER BY score
                """, (fts_query,))

                for row in cursor.fetchall():
                    matched_text = self._get_matched_text(
                        row, ['title', 'description']
                    )
                    results.append(SearchResult(
                        entity_type='topic',
                        entity_id=row['id'],
                        title=row['title'],
                        description=row['description'] or '',
                        matched_text=matched_text,
                        relevance_score=-(row['score'] or 0)
                    ))
            except sqlite3.Error:
                results = []

        return results or self._fallback_topics(keyword)

    def _search_lessons(self, keyword: str) -> List[SearchResult]:
        """Search in lessons using FTS."""
        results = []
        fts_query = self._fts_query(keyword)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT l.id, l.title, l.description, l.duration_hours,
                           lt.name as lesson_type_name,
                           bm25(lessons_fts) as score
                    FROM lessons l
                    LEFT JOIN lesson_types lt ON l.lesson_type_id = lt.id
                    JOIN lessons_fts ON l.id = lessons_fts.rowid
                    WHERE lessons_fts MATCH ?
                    ORDER BY score
                """, (fts_query,))

                for row in cursor.fetchall():
                    matched_text = self._get_matched_text(
                        row, ['title', 'description', 'lesson_type_name']
                    )
                    lesson_type = row['lesson_type_name'] or ''
                    description = f"{row['description'] or ''} ({row['duration_hours']}h)"
                    if lesson_type:
                        description = f"{lesson_type} | {description}"
                    results.append(SearchResult(
                        entity_type='lesson',
                        entity_id=row['id'],
                        title=row['title'],
                        description=description,
                        matched_text=matched_text,
                        relevance_score=-(row['score'] or 0)
                    ))
            except sqlite3.Error:
                results = []

        return results or self._fallback_lessons(keyword)

    def _search_questions(self, keyword: str) -> List[SearchResult]:
        """Search in questions using FTS."""
        results = []
        fts_query = self._fts_query(keyword)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT q.id, q.content, q.answer, q.difficulty_level, 
                           bm25(questions_fts) as score
                    FROM questions q
                    JOIN questions_fts ON q.id = questions_fts.rowid
                    WHERE questions_fts MATCH ?
                    ORDER BY score
                """, (fts_query,))

                for row in cursor.fetchall():
                    matched_text = self._get_matched_text(row, ['content'])
                    description = f"Difficulty: {row['difficulty_level']}"
                    results.append(SearchResult(
                        entity_type='question',
                        entity_id=row['id'],
                        title=row['content'][:100] + '...' if len(row['content']) > 100 else row['content'],
                        description=description,
                        matched_text=matched_text,
                        relevance_score=-(row['score'] or 0)
                    ))
            except sqlite3.Error:
                results = []

        return results or self._fallback_questions(keyword)

    def _search_materials(self, keyword: str) -> List[SearchResult]:
        """Search in methodical materials using FTS."""
        results = []
        fts_query = self._fts_query(keyword)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT m.id, m.title, m.description, m.material_type, 
                           m.file_name, bm25(materials_fts) as score
                    FROM methodical_materials m
                    JOIN materials_fts ON m.id = materials_fts.rowid
                    WHERE materials_fts MATCH ?
                    ORDER BY score
                """, (fts_query,))

                for row in cursor.fetchall():
                    matched_text = self._get_matched_text(
                        row, ['title', 'description', 'file_name']
                    )
                    description = f"{row['material_type']} - {row['description'] or ''}"
                    if row['file_name']:
                        description += f" | File: {row['file_name']}"
                    results.append(SearchResult(
                        entity_type='material',
                        entity_id=row['id'],
                        title=row['title'],
                        description=description.strip(' -'),
                        matched_text=matched_text,
                        relevance_score=-(row['score'] or 0)
                    ))
            except sqlite3.Error:
                results = []

        return results or self._fallback_materials(keyword)

    def _get_matched_text(self, row: Dict[str, Any], fields: List[str]) -> str:
        """
        Extract matched text from search result.

        Args:
            row: Database row
            fields: List of fields to check for matches

        Returns:
            str: Concatenated matched text
        """
        matched_parts = []
        for field in fields:
            value = row[field] if field in row.keys() else None
            if value:
                matched_parts.append(str(value))
        return ' | '.join(matched_parts)

    def _fallback_teachers(self, keyword: str) -> List[SearchResult]:
        results = []
        for teacher in self.teacher_repo.search(keyword):
            matched_text = " | ".join(
                value for value in [
                    teacher.full_name,
                    teacher.military_rank or "",
                    teacher.position or "",
                    teacher.department or "",
                    teacher.email or "",
                    teacher.phone or "",
                ] if value
            )
            description = f"{teacher.position or ''} - {teacher.department or ''}"
            results.append(SearchResult(
                entity_type='teacher',
                entity_id=teacher.id,
                title=teacher.full_name,
                description=description.strip(' -'),
                matched_text=matched_text,
                relevance_score=0.0
            ))
        return results

    def _fallback_programs(self, keyword: str) -> List[SearchResult]:
        results = []
        for program in self.program_repo.search(keyword):
            matched_text = " | ".join(
                value for value in [program.name, program.description or "", program.level or ""] if value
            )
            description = f"{program.level or ''} - {program.description or ''}"
            results.append(SearchResult(
                entity_type='program',
                entity_id=program.id,
                title=program.name,
                description=description.strip(' -'),
                matched_text=matched_text,
                relevance_score=0.0
            ))
        return results

    def _fallback_disciplines(self, keyword: str) -> List[SearchResult]:
        results = []
        for discipline in self.discipline_repo.search(keyword):
            matched_text = " | ".join(
                value for value in [discipline.name, discipline.description or ""] if value
            )
            results.append(SearchResult(
                entity_type='discipline',
                entity_id=discipline.id,
                title=discipline.name,
                description=discipline.description or "",
                matched_text=matched_text,
                relevance_score=0.0
            ))
        return results

    def _fallback_topics(self, keyword: str) -> List[SearchResult]:
        results = []
        for topic in self.topic_repo.search(keyword):
            matched_text = " | ".join(
                value for value in [topic.title, topic.description or ""] if value
            )
            results.append(SearchResult(
                entity_type='topic',
                entity_id=topic.id,
                title=topic.title,
                description=topic.description or "",
                matched_text=matched_text,
                relevance_score=0.0
            ))
        return results

    def _fallback_lessons(self, keyword: str) -> List[SearchResult]:
        results = []
        for lesson in self.lesson_repo.search(keyword):
            matched_text = " | ".join(
                value for value in [
                    lesson.title,
                    lesson.description or "",
                    lesson.lesson_type_name or "",
                ] if value
            )
            lesson_type = lesson.lesson_type_name or ""
            description = f"{lesson.description or ''} ({lesson.duration_hours}h)"
            if lesson_type:
                description = f"{lesson_type} | {description}"
            results.append(SearchResult(
                entity_type='lesson',
                entity_id=lesson.id,
                title=lesson.title,
                description=description,
                matched_text=matched_text,
                relevance_score=0.0
            ))
        return results

    def _fallback_questions(self, keyword: str) -> List[SearchResult]:
        results = []
        for question in self.question_repo.search(keyword):
            matched_text = " | ".join(
                value for value in [question.content] if value
            )
            description = f"Difficulty: {question.difficulty_level}"
            results.append(SearchResult(
                entity_type='question',
                entity_id=question.id,
                title=question.content[:100] + '...' if len(question.content) > 100 else question.content,
                description=description,
                matched_text=matched_text,
                relevance_score=0.0
            ))
        return results

    def _fallback_materials(self, keyword: str) -> List[SearchResult]:
        results = []
        for material in self.material_repo.search(keyword):
            matched_text = " | ".join(
                value for value in [material.title, material.description or "", material.file_name or ""] if value
            )
            description = f"{material.material_type} - {material.description or ''}"
            if material.file_name:
                description += f" | File: {material.file_name}"
            results.append(SearchResult(
                entity_type='material',
                entity_id=material.id,
                title=material.title,
                description=description.strip(' -'),
                matched_text=matched_text,
                relevance_score=0.0
            ))
        return results
