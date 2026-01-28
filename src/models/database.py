"""Database management for educational program application."""
import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
from ..services.app_paths import get_app_base_dir, get_database_dir

class Database:
    """SQLite database manager for educational program data."""

    def __init__(self, db_path: str = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. If None, uses default path.
        """
        if db_path is None:
            database_dir = get_database_dir()
            new_path = database_dir / "education.db"
            legacy_path = get_app_base_dir() / "data" / "education.db"
            if legacy_path.exists() and not new_path.exists():
                new_path.parent.mkdir(parents=True, exist_ok=True)
                new_path.write_bytes(legacy_path.read_bytes())
            db_path = str(new_path)

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
        conn.execute("PRAGMA foreign_keys = ON")
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
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Teachers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    military_rank TEXT,
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

            # Disciplines table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS disciplines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    order_index INTEGER DEFAULT 0,
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

            # Lesson types table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lesson_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
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
                    lesson_type_id INTEGER,
                    classroom_hours REAL,
                    self_study_hours REAL,
                    order_index INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lesson_type_id) REFERENCES lesson_types(id)
                        ON DELETE SET NULL
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
                    original_filename TEXT,
                    stored_filename TEXT,
                    relative_path TEXT,
                    file_type TEXT,
                    file_path TEXT,
                    file_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Program-Discipline relationship (many-to-many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS program_disciplines (
                    program_id INTEGER NOT NULL,
                    discipline_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (program_id, discipline_id),
                    FOREIGN KEY (program_id) REFERENCES educational_programs(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
                        ON DELETE CASCADE
                )
            """)

            # Discipline-Topic relationship (many-to-many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS discipline_topics (
                    discipline_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    PRIMARY KEY (discipline_id, topic_id),
                    FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (topic_id) REFERENCES topics(id)
                        ON DELETE CASCADE
                )
            """)

            # Program-Topic relationship (legacy, kept for compatibility)
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
                        ('program', 'discipline', 'topic', 'lesson')),
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
                CREATE INDEX IF NOT EXISTS idx_disciplines_name
                ON disciplines(name)
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
                    full_name, military_rank, position, department, email,
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
                CREATE VIRTUAL TABLE IF NOT EXISTS disciplines_fts USING fts5(
                    name, description,
                    content='disciplines', content_rowid='id'
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
            self._ensure_schema_version(cursor)
            self._ensure_default_lesson_types(cursor)

    def _ensure_schema_version(self, cursor) -> None:
        """Ensure schema migrations are applied."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL
            )
        """)
        cursor.execute("SELECT MAX(version) as version FROM schema_migrations")
        row = cursor.fetchone()
        current_version = row["version"] if row and row["version"] is not None else 1

        if current_version < 2:
            self._migrate_to_disciplines(cursor)
            cursor.execute("INSERT INTO schema_migrations (version) VALUES (2)")
            current_version = 2

        if current_version < 3:
            self._migrate_to_lesson_types(cursor)
            cursor.execute("INSERT INTO schema_migrations (version) VALUES (3)")
            current_version = 3

        if current_version < 4:
            self._migrate_to_lesson_hours(cursor)
            cursor.execute("INSERT INTO schema_migrations (version) VALUES (4)")
            current_version = 4

        if current_version < 5:
            self._migrate_to_teacher_ranks(cursor)
            cursor.execute("INSERT INTO schema_migrations (version) VALUES (5)")
            current_version = 5

        if current_version < 6:
            self._migrate_to_material_storage(cursor)
            cursor.execute("INSERT INTO schema_migrations (version) VALUES (6)")

    def _migrate_to_disciplines(self, cursor) -> None:
        """Migrate existing program->topic links into disciplines."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disciplines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS program_disciplines (
                program_id INTEGER NOT NULL,
                discipline_id INTEGER NOT NULL,
                order_index INTEGER DEFAULT 0,
                PRIMARY KEY (program_id, discipline_id),
                FOREIGN KEY (program_id) REFERENCES educational_programs(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
                    ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discipline_topics (
                discipline_id INTEGER NOT NULL,
                topic_id INTEGER NOT NULL,
                order_index INTEGER DEFAULT 0,
                PRIMARY KEY (discipline_id, topic_id),
                FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("SELECT COUNT(*) as count FROM disciplines")
        existing_disciplines = cursor.fetchone()["count"]
        if existing_disciplines == 0:
            cursor.execute("SELECT id, name FROM educational_programs")
            programs = cursor.fetchall()
            for program in programs:
                discipline_name = f"Discipline for {program['name']}"
                cursor.execute("""
                    INSERT INTO disciplines (name, description, order_index)
                    VALUES (?, ?, 0)
                """, (discipline_name, ""))
                discipline_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO program_disciplines (program_id, discipline_id, order_index)
                    VALUES (?, ?, 0)
                """, (program["id"], discipline_id))
                cursor.execute("""
                    SELECT topic_id, order_index FROM program_topics
                    WHERE program_id = ?
                    ORDER BY order_index
                """, (program["id"],))
                for topic_row in cursor.fetchall():
                    cursor.execute("""
                        INSERT OR IGNORE INTO discipline_topics (discipline_id, topic_id, order_index)
                        VALUES (?, ?, ?)
                    """, (discipline_id, topic_row["topic_id"], topic_row["order_index"]))

        # Update material associations to allow discipline
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='material_associations'")
        if cursor.fetchone():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS material_associations_new (
                    material_id INTEGER NOT NULL,
                    entity_type TEXT NOT NULL CHECK(entity_type IN
                        ('program', 'discipline', 'topic', 'lesson')),
                    entity_id INTEGER NOT NULL,
                    PRIMARY KEY (material_id, entity_type, entity_id),
                    FOREIGN KEY (material_id) REFERENCES methodical_materials(id)
                        ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                INSERT OR IGNORE INTO material_associations_new (material_id, entity_type, entity_id)
                SELECT material_id, entity_type, entity_id FROM material_associations
            """)
            cursor.execute("DROP TABLE material_associations")
            cursor.execute("ALTER TABLE material_associations_new RENAME TO material_associations")

        # Ensure discipline FTS and triggers exist
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS disciplines_fts USING fts5(
                name, description,
                content='disciplines', content_rowid='id'
            )
        """)

    def _ensure_default_lesson_types(self, cursor) -> None:
        """Seed default lesson types if none exist."""
        cursor.execute("SELECT COUNT(*) as count FROM lesson_types")
        if cursor.fetchone()["count"] > 0:
            return
        default_types = [
            "Самостійна робота",
            "Лекція",
            "Групове заняття",
            "Практичне заняття",
            "Семінар",
            "Контрольне заняття",
        ]
        for name in default_types:
            cursor.execute("INSERT INTO lesson_types (name) VALUES (?)", (name,))

    def _migrate_to_lesson_types(self, cursor) -> None:
        """Add lesson types table and lesson_type_id column."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("PRAGMA table_info(lessons)")
        columns = {row["name"] for row in cursor.fetchall()}
        if "lesson_type_id" not in columns:
            cursor.execute("ALTER TABLE lessons ADD COLUMN lesson_type_id INTEGER")
        self._ensure_default_lesson_types(cursor)
        cursor.execute("SELECT id FROM lesson_types ORDER BY id LIMIT 1")
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                UPDATE lessons
                SET lesson_type_id = ?
                WHERE lesson_type_id IS NULL
            """, (row["id"],))

    def _migrate_to_lesson_hours(self, cursor) -> None:
        """Add classroom/self-study hour columns to lessons."""
        cursor.execute("PRAGMA table_info(lessons)")
        columns = {row["name"] for row in cursor.fetchall()}
        if "classroom_hours" not in columns:
            cursor.execute("ALTER TABLE lessons ADD COLUMN classroom_hours REAL")
        if "self_study_hours" not in columns:
            cursor.execute("ALTER TABLE lessons ADD COLUMN self_study_hours REAL")

    def _migrate_to_teacher_ranks(self, cursor) -> None:
        """Add military rank to teachers and rebuild teacher FTS."""
        cursor.execute("PRAGMA table_info(teachers)")
        columns = {row["name"] for row in cursor.fetchall()}
        if "military_rank" not in columns:
            cursor.execute("ALTER TABLE teachers ADD COLUMN military_rank TEXT")

        cursor.execute("DROP TABLE IF EXISTS teachers_fts")
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS teachers_fts USING fts5(
                full_name, military_rank, position, department, email,
                content='teachers', content_rowid='id'
            )
        """)
        cursor.execute("""
            INSERT INTO teachers_fts(rowid, full_name, military_rank, position, department, email)
            SELECT id, full_name, military_rank, position, department, email
            FROM teachers
        """)

    def _migrate_to_material_storage(self, cursor) -> None:
        """Add storage metadata fields to methodical materials."""
        cursor.execute("PRAGMA table_info(methodical_materials)")
        columns = {row["name"] for row in cursor.fetchall()}
        if "original_filename" not in columns:
            cursor.execute("ALTER TABLE methodical_materials ADD COLUMN original_filename TEXT")
        if "stored_filename" not in columns:
            cursor.execute("ALTER TABLE methodical_materials ADD COLUMN stored_filename TEXT")
        if "relative_path" not in columns:
            cursor.execute("ALTER TABLE methodical_materials ADD COLUMN relative_path TEXT")
        if "file_type" not in columns:
            cursor.execute("ALTER TABLE methodical_materials ADD COLUMN file_type TEXT")
    def _create_fts_triggers(self, cursor):
        """Create triggers to maintain FTS tables."""
        # Teachers triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS teachers_ai AFTER INSERT ON teachers BEGIN
                INSERT INTO teachers_fts(rowid, full_name, military_rank, position, department, email)
                VALUES (NEW.id, NEW.full_name, NEW.military_rank, NEW.position, NEW.department, NEW.email);
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
                SET full_name = NEW.full_name, military_rank = NEW.military_rank,
                    position = NEW.position, department = NEW.department, email = NEW.email
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

        # Disciplines triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS disciplines_ai AFTER INSERT ON disciplines BEGIN
                INSERT INTO disciplines_fts(rowid, name, description)
                VALUES (NEW.id, NEW.name, NEW.description);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS disciplines_ad AFTER DELETE ON disciplines BEGIN
                DELETE FROM disciplines_fts WHERE rowid = OLD.id;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS disciplines_au AFTER UPDATE ON disciplines BEGIN
                UPDATE disciplines_fts
                SET name = NEW.name, description = NEW.description
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
                    ORDER BY bm25(teachers_fts)
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
                    ORDER BY bm25(programs_fts)
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
                    ORDER BY bm25(topics_fts)
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
                    ORDER BY bm25(lessons_fts)
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
                    ORDER BY bm25(questions_fts)
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
                    ORDER BY bm25(materials_fts)
                    LIMIT 50
                """, (search_query,))
                results.extend([dict(row) for row in cursor.fetchall()])

        return results
