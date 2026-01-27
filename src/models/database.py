"""Database management for educational program application."""
import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

class Database:
    """SQLite database manager for educational program data."""

    def __init__(self, db_path: str = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. If None, uses default path.
        """
        if db_path is None:
            # Default to data directory in application root
            app_dir = Path(__file__).parent.parent.parent
            data_dir = app_dir / 'data'
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / 'education.db')

        self.db_path = db_path
        self._ensure_database_exists()

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: Active database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _ensure_database_exists(self):
        """Create database and tables if they don't exist."""
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Teachers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    position TEXT,
                    department TEXT,
                    email TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Educational Programs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS educational_programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    level TEXT,
                    duration_hours INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Topics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    order_index INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Lessons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    duration_hours REAL DEFAULT 1.0,
                    order_index INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Questions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    answer TEXT,
                    difficulty_level INTEGER DEFAULT 1,
                    order_index INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Methodical Materials table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS methodical_materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    material_type TEXT NOT NULL CHECK(material_type IN 
                        ('plan', 'guide', 'presentation', 'attachment')),
                    description TEXT,
                    file_path TEXT,
                    file_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Program-Topic relationship (many-to-many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS program_topics (
                    program_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (program_id, topic_id),
                    FOREIGN KEY (program_id) REFERENCES educational_programs(id) 
                        ON DELETE CASCADE,
                    FOREIGN KEY (topic_id) REFERENCES topics(id) 
                        ON DELETE CASCADE
                )
            """)

            # Topic-Lesson relationship (many-to-many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topic_lessons (
                    topic_id INTEGER NOT NULL,
                    lesson_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (topic_id, lesson_id),
                    FOREIGN KEY (topic_id) REFERENCES topics(id) 
                        ON DELETE CASCADE,
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id) 
                        ON DELETE CASCADE
                )
            """)

            # Lesson-Question relationship (many-to-many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lesson_questions (
                    lesson_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (lesson_id, question_id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id) 
                        ON DELETE CASCADE,
                    FOREIGN KEY (question_id) REFERENCES questions(id) 
                        ON DELETE CASCADE
                )
            """)

            # Teacher-Material relationship (many-to-many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teacher_materials (
                    teacher_id INTEGER NOT NULL,
                    material_id INTEGER NOT NULL,
                    role TEXT DEFAULT 'author',
                    PRIMARY KEY (teacher_id, material_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id) 
                        ON DELETE CASCADE,
                    FOREIGN KEY (material_id) REFERENCES methodical_materials(id) 
                        ON DELETE CASCADE
                )
            """)

            # Material associations (which entity the material belongs to)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS material_associations (
                    material_id INTEGER NOT NULL,
                    entity_type TEXT NOT NULL CHECK(entity_type IN 
                        ('program', 'topic', 'lesson')),
                    entity_id INTEGER NOT NULL,
                    PRIMARY KEY (material_id, entity_type, entity_id),
                    FOREIGN KEY (material_id) REFERENCES methodical_materials(id) 
                        ON DELETE CASCADE
                )
            """)

            # Create indexes for better search performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_teachers_name 
                ON teachers(full_name)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_programs_name 
                ON educational_programs(name)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_topics_title 
                ON topics(title)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lessons_title 
                ON lessons(title)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_questions_content 
                ON questions(content)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_materials_title 
                ON methodical_materials(title)
            """)

            # Create FTS5 virtual tables for full-text search
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS teachers_fts USING fts5(
                    full_name, position, department, email, 
                    content='teachers', content_rowid='id'
                )
            """)

            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS programs_fts USING fts5(
                    name, description, level,
                    content='educational_programs', content_rowid='id'
                )
            """)

            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS topics_fts USING fts5(
                    title, description,
                    content='topics', content_rowid='id'
                )
            """)

            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS lessons_fts USING fts5(
                    title, description,
                    content='lessons', content_rowid='id'
                )
            """)

            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS questions_fts USING fts5(
                    content, answer,
                    content='questions', content_rowid='id'
                )
            """)

            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS materials_fts USING fts5(
                    title, description, file_name,
                    content='methodical_materials', content_rowid='id'
                )
            """)

            # Create triggers to keep FTS tables in sync
            self._create_fts_triggers(cursor)

    def _create_fts_triggers(self, cursor):
        """Create triggers to maintain FTS tables."""
        # Teachers triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS teachers_ai AFTER INSERT ON teachers BEGIN
                INSERT INTO teachers_fts(rowid, full_name, position, department, email)
                VALUES (NEW.id, NEW.full_name, NEW.position, NEW.department, NEW.email);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS teachers_ad AFTER DELETE ON teachers BEGIN
                DELETE FROM teachers_fts WHERE rowid = OLD.id;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS teachers_au AFTER UPDATE ON teachers BEGIN
                UPDATE teachers_fts 
                SET full_name = NEW.full_name, position = NEW.position, 
                    department = NEW.department, email = NEW.email
                WHERE rowid = NEW.id;
            END
        """)

        # Programs triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS programs_ai AFTER INSERT ON educational_programs BEGIN
                INSERT INTO programs_fts(rowid, name, description, level)
                VALUES (NEW.id, NEW.name, NEW.description, NEW.level);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS programs_ad AFTER DELETE ON educational_programs BEGIN
                DELETE FROM programs_fts WHERE rowid = OLD.id;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS programs_au AFTER UPDATE ON educational_programs BEGIN
                UPDATE programs_fts 
                SET name = NEW.name, description = NEW.description, level = NEW.level
                WHERE rowid = NEW.id;
            END
        """)

        # Topics triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS topics_ai AFTER INSERT ON topics BEGIN
                INSERT INTO topics_fts(rowid, title, description)
                VALUES (NEW.id, NEW.title, NEW.description);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS topics_ad AFTER DELETE ON topics BEGIN
                DELETE FROM topics_fts WHERE rowid = OLD.id;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS topics_au AFTER UPDATE ON topics BEGIN
                UPDATE topics_fts 
                SET title = NEW.title, description = NEW.description
                WHERE rowid = NEW.id;
            END
        """)

        # Lessons triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS lessons_ai AFTER INSERT ON lessons BEGIN
                INSERT INTO lessons_fts(rowid, title, description)
                VALUES (NEW.id, NEW.title, NEW.description);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS lessons_ad AFTER DELETE ON lessons BEGIN
                DELETE FROM lessons_fts WHERE rowid = OLD.id;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS lessons_au AFTER UPDATE ON lessons BEGIN
                UPDATE lessons_fts 
                SET title = NEW.title, description = NEW.description
                WHERE rowid = NEW.id;
            END
        """)

        # Questions triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS questions_ai AFTER INSERT ON questions BEGIN
                INSERT INTO questions_fts(rowid, content, answer)
                VALUES (NEW.id, NEW.content, NEW.answer);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS questions_ad AFTER DELETE ON questions BEGIN
                DELETE FROM questions_fts WHERE rowid = OLD.id;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS questions_au AFTER UPDATE ON questions BEGIN
                UPDATE questions_fts 
                SET content = NEW.content, answer = NEW.answer
                WHERE rowid = NEW.id;
            END
        """)

        # Materials triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS materials_ai AFTER INSERT ON methodical_materials BEGIN
                INSERT INTO materials_fts(rowid, title, description, file_name)
                VALUES (NEW.id, NEW.title, NEW.description, NEW.file_name);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS materials_ad AFTER DELETE ON methodical_materials BEGIN
                DELETE FROM materials_fts WHERE rowid = OLD.id;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS materials_au AFTER UPDATE ON methodical_materials BEGIN
                UPDATE materials_fts 
                SET title = NEW.title, description = NEW.description, file_name = NEW.file_name
                WHERE rowid = NEW.id;
            END
        """)

    def search(self, query: str, entity_type: str = None) -> List[Dict[str, Any]]:
        """
        Perform full-text search across all entities.

        Args:
            query: Search query string
            entity_type: Optional entity type filter (teacher, program, topic, lesson, question, material)

        Returns:
            List of search results with entity type and data
        """
        if not query or len(query.strip()) < 2:
            return []

        results = []
        search_query = query.strip()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Search teachers
            if entity_type is None or entity_type == 'teacher':
                cursor.execute("""
                    SELECT 'teacher' as type, t.id, t.full_name, t.position, t.department
                    FROM teachers_fts f
                    JOIN teachers t ON t.id = f.rowid
                    WHERE teachers_fts MATCH ?
                    ORDER BY rank
                    LIMIT 50
                """, (search_query,))
                results.extend([dict(row) for row in cursor.fetchall()])

            # Search programs
            if entity_type is None or entity_type == 'program':
                cursor.execute("""
                    SELECT 'program' as type, p.id, p.name, p.description, p.level
                    FROM programs_fts f
                    JOIN educational_programs p ON p.id = f.rowid
                    WHERE programs_fts MATCH ?
                    ORDER BY rank
                    LIMIT 50
                """, (search_query,))
                results.extend([dict(row) for row in cursor.fetchall()])

            # Search topics
            if entity_type is None or entity_type == 'topic':
                cursor.execute("""
                    SELECT 'topic' as type, t.id, t.title, t.description
                    FROM topics_fts f
                    JOIN topics t ON t.id = f.rowid
                    WHERE topics_fts MATCH ?
                    ORDER BY rank
                    LIMIT 50
                """, (search_query,))
                results.extend([dict(row) for row in cursor.fetchall()])

            # Search lessons
            if entity_type is None or entity_type == 'lesson':
                cursor.execute("""
                    SELECT 'lesson' as type, l.id, l.title, l.description
                    FROM lessons_fts f
                    JOIN lessons l ON l.id = f.rowid
                    WHERE lessons_fts MATCH ?
                    ORDER BY rank
                    LIMIT 50
                """, (search_query,))
                results.extend([dict(row) for row in cursor.fetchall()])

            # Search questions
            if entity_type is None or entity_type == 'question':
                cursor.execute("""
                    SELECT 'question' as type, q.id, q.content, q.answer
                    FROM questions_fts f
                    JOIN questions q ON q.id = f.rowid
                    WHERE questions_fts MATCH ?
                    ORDER BY rank
                    LIMIT 50
                """, (search_query,))
                results.extend([dict(row) for row in cursor.fetchall()])

            # Search materials
            if entity_type is None or entity_type == 'material':
                cursor.execute("""
                    SELECT 'material' as type, m.id, m.title, m.description, 
                           m.material_type, m.file_name
                    FROM materials_fts f
                    JOIN methodical_materials m ON m.id = f.rowid
                    WHERE materials_fts MATCH ?
                    ORDER BY rank
                    LIMIT 50
                """, (search_query,))
                results.extend([dict(row) for row in cursor.fetchall()])

        return results
