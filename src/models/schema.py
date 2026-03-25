"""Shared SQLite schema metadata for bootstrap and migrations."""

SCHEMA_MIGRATIONS = (
    (2, "_migrate_to_disciplines"),
    (3, "_migrate_to_lesson_types"),
    (4, "_migrate_to_lesson_hours"),
    (5, "_migrate_to_teacher_ranks"),
    (6, "_migrate_to_material_storage"),
    (7, "_migrate_to_material_types"),
    (8, "_migrate_to_teacher_disciplines"),
    (9, "_migrate_to_program_year"),
    (10, "_migrate_to_lesson_type_synonyms"),
    (11, "_rebuild_all_fts"),
)

CORE_TABLE_STATEMENTS = (
    """
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
    """,
    """
    CREATE TABLE IF NOT EXISTS educational_programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        level TEXT,
        year INTEGER NOT NULL DEFAULT 0,
        duration_hours INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS disciplines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lesson_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        synonyms TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
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
    """,
    """
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        answer TEXT,
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS material_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS methodical_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        material_type TEXT NOT NULL,
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
    """,
    """
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
    """,
    """
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
    """,
    """
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
    """,
    """
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
    """,
    """
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
    """,
    """
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
    """,
    """
    CREATE TABLE IF NOT EXISTS teacher_disciplines (
        teacher_id INTEGER NOT NULL,
        discipline_id INTEGER NOT NULL,
        PRIMARY KEY (teacher_id, discipline_id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            ON DELETE CASCADE,
        FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
            ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS material_associations (
        material_id INTEGER NOT NULL,
        entity_type TEXT NOT NULL CHECK(entity_type IN
            ('program', 'discipline', 'topic', 'lesson')),
        entity_id INTEGER NOT NULL,
        PRIMARY KEY (material_id, entity_type, entity_id),
        FOREIGN KEY (material_id) REFERENCES methodical_materials(id)
            ON DELETE CASCADE
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE INDEX IF NOT EXISTS idx_teachers_name ON teachers(full_name)",
    "CREATE INDEX IF NOT EXISTS idx_programs_name ON educational_programs(name)",
    "CREATE INDEX IF NOT EXISTS idx_topics_title ON topics(title)",
    "CREATE INDEX IF NOT EXISTS idx_disciplines_name ON disciplines(name)",
    "CREATE INDEX IF NOT EXISTS idx_lessons_title ON lessons(title)",
    "CREATE INDEX IF NOT EXISTS idx_questions_content ON questions(content)",
    "CREATE INDEX IF NOT EXISTS idx_materials_title ON methodical_materials(title)",
)

FTS_TABLE_STATEMENTS = (
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS teachers_fts USING fts5(
        full_name, military_rank, position, department, email,
        content='teachers', content_rowid='id'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS programs_fts USING fts5(
        name, description, level,
        content='educational_programs', content_rowid='id'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS topics_fts USING fts5(
        title, description,
        content='topics', content_rowid='id'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS disciplines_fts USING fts5(
        name, description,
        content='disciplines', content_rowid='id'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS lessons_fts USING fts5(
        title, description,
        content='lessons', content_rowid='id'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS questions_fts USING fts5(
        content, answer,
        content='questions', content_rowid='id'
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS materials_fts USING fts5(
        title, description, file_name,
        content='methodical_materials', content_rowid='id'
    )
    """,
)
