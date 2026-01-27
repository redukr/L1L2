"""Search service for full-text search across all entities."""
from typing import List, Dict, Any
from ..models.entities import SearchResult
from ..models.database import Database


class SearchService:
    """Service for performing full-text searches across all entities."""

    def __init__(self, database: Database):
        """
        Initialize search service.

        Args:
            database: Database instance
        """
        self.db = database

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
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.full_name, t.position, t.department, 
                       t.email, t.phone, bm25(teachers_fts) as score
                FROM teachers t
                JOIN teachers_fts ON t.id = teachers_fts.rowid
                WHERE teachers_fts MATCH ?
                ORDER BY score
            """, (keyword,))

            for row in cursor.fetchall():
                matched_text = self._get_matched_text(
                    row, ['full_name', 'position', 'department', 'email', 'phone']
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

        return results

    def _search_programs(self, keyword: str) -> List[SearchResult]:
        """Search in educational programs using FTS."""
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.name, p.description, p.level, 
                       p.duration_hours, bm25(programs_fts) as score
                FROM educational_programs p
                JOIN programs_fts ON p.id = programs_fts.rowid
                WHERE programs_fts MATCH ?
                ORDER BY score
            """, (keyword,))

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
<<<<<<< ours
                ))

        return results

    def _search_disciplines(self, keyword: str) -> List[SearchResult]:
        """Search in disciplines using FTS."""
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, d.name, d.description, bm25(disciplines_fts) as score
                FROM disciplines d
                JOIN disciplines_fts ON d.id = disciplines_fts.rowid
                WHERE disciplines_fts MATCH ?
                ORDER BY score
            """, (keyword,))

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
=======
>>>>>>> theirs
                ))

        return results

    def _search_topics(self, keyword: str) -> List[SearchResult]:
        """Search in topics using FTS."""
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.title, t.description, bm25(topics_fts) as score
                FROM topics t
                JOIN topics_fts ON t.id = topics_fts.rowid
                WHERE topics_fts MATCH ?
                ORDER BY score
            """, (keyword,))

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

        return results

    def _search_lessons(self, keyword: str) -> List[SearchResult]:
        """Search in lessons using FTS."""
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id, l.title, l.description, l.duration_hours, 
                       bm25(lessons_fts) as score
                FROM lessons l
                JOIN lessons_fts ON l.id = lessons_fts.rowid
                WHERE lessons_fts MATCH ?
                ORDER BY score
            """, (keyword,))

            for row in cursor.fetchall():
                matched_text = self._get_matched_text(
                    row, ['title', 'description']
                )
                description = f"{row['description'] or ''} ({row['duration_hours']}h)"
                results.append(SearchResult(
                    entity_type='lesson',
                    entity_id=row['id'],
                    title=row['title'],
                    description=description,
                    matched_text=matched_text,
                    relevance_score=-(row['score'] or 0)
                ))

        return results

    def _search_questions(self, keyword: str) -> List[SearchResult]:
        """Search in questions using FTS."""
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.id, q.content, q.answer, q.difficulty_level, 
                       bm25(questions_fts) as score
                FROM questions q
                JOIN questions_fts ON q.id = questions_fts.rowid
                WHERE questions_fts MATCH ?
                ORDER BY score
            """, (keyword,))

            for row in cursor.fetchall():
                matched_text = self._get_matched_text(
                    row, ['content', 'answer']
                )
                description = f"Difficulty: {row['difficulty_level']}"
                if row['answer']:
                    description += f" | Answer: {row['answer'][:100]}..."
                results.append(SearchResult(
                    entity_type='question',
                    entity_id=row['id'],
                    title=row['content'][:100] + '...' if len(row['content']) > 100 else row['content'],
                    description=description,
                    matched_text=matched_text,
                    relevance_score=-(row['score'] or 0)
                ))

        return results

    def _search_materials(self, keyword: str) -> List[SearchResult]:
        """Search in methodical materials using FTS."""
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.id, m.title, m.description, m.material_type, 
                       m.file_name, bm25(materials_fts) as score
                FROM methodical_materials m
                JOIN materials_fts ON m.id = materials_fts.rowid
                WHERE materials_fts MATCH ?
                ORDER BY score
            """, (keyword,))

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

        return results

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
<<<<<<< ours
            value = row[field] if field in row.keys() else None
=======
            value = None
            if hasattr(row, 'keys'):
                if field in row.keys():
                    value = row[field]
            elif isinstance(row, dict):
                value = row.get(field)
            else:
                value = getattr(row, field, None)
>>>>>>> theirs
            if value:
                matched_parts.append(str(value))
        return ' | '.join(matched_parts)
