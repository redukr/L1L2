"""DDL fragments for internet sync MySQL schema bootstrap."""

from __future__ import annotations


MYSQL_SYNC_SCHEMA_DDL: list[str] = [
    """
    CREATE TABLE IF NOT EXISTS teachers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name TEXT NOT NULL,
        order_index INT DEFAULT 0,
        military_rank TEXT NULL,
        position TEXT NULL,
        department TEXT NULL,
        email TEXT NULL,
        phone TEXT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS educational_programs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NULL,
        level TEXT NULL,
        year INT NOT NULL DEFAULT 0,
        duration_hours INT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS disciplines (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NULL,
        order_index INT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS topics (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NULL,
        order_index INT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS lesson_types (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        synonyms TEXT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS lessons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NULL,
        duration_hours DOUBLE DEFAULT 1.0,
        lesson_type_id INT NULL,
        classroom_hours DOUBLE NULL,
        self_study_hours DOUBLE NULL,
        order_index INT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_lessons_lesson_type_id (lesson_type_id),
        CONSTRAINT fk_lessons_lesson_type
            FOREIGN KEY (lesson_type_id) REFERENCES lesson_types(id)
            ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        content TEXT NOT NULL,
        answer TEXT NULL,
        order_index INT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS material_types (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS methodical_materials (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title TEXT NOT NULL,
        material_type TEXT NOT NULL,
        description TEXT NULL,
        original_filename TEXT NULL,
        stored_filename TEXT NULL,
        relative_path TEXT NULL,
        file_type TEXT NULL,
        file_path TEXT NULL,
        file_name TEXT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS program_disciplines (
        program_id INT NOT NULL,
        discipline_id INT NOT NULL,
        order_index INT DEFAULT 0,
        PRIMARY KEY (program_id, discipline_id),
        CONSTRAINT fk_pd_program
            FOREIGN KEY (program_id) REFERENCES educational_programs(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_pd_discipline
            FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS discipline_topics (
        discipline_id INT NOT NULL,
        topic_id INT NOT NULL,
        order_index INT DEFAULT 0,
        PRIMARY KEY (discipline_id, topic_id),
        CONSTRAINT fk_dt_discipline
            FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_dt_topic
            FOREIGN KEY (topic_id) REFERENCES topics(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS program_topics (
        program_id INT NOT NULL,
        topic_id INT NOT NULL,
        order_index INT DEFAULT 0,
        PRIMARY KEY (program_id, topic_id),
        CONSTRAINT fk_pt_program
            FOREIGN KEY (program_id) REFERENCES educational_programs(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_pt_topic
            FOREIGN KEY (topic_id) REFERENCES topics(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS topic_lessons (
        topic_id INT NOT NULL,
        lesson_id INT NOT NULL,
        order_index INT DEFAULT 0,
        PRIMARY KEY (topic_id, lesson_id),
        CONSTRAINT fk_tl_topic
            FOREIGN KEY (topic_id) REFERENCES topics(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_tl_lesson
            FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS lesson_questions (
        lesson_id INT NOT NULL,
        question_id INT NOT NULL,
        order_index INT DEFAULT 0,
        PRIMARY KEY (lesson_id, question_id),
        CONSTRAINT fk_lq_lesson
            FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_lq_question
            FOREIGN KEY (question_id) REFERENCES questions(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS teacher_materials (
        teacher_id INT NOT NULL,
        material_id INT NOT NULL,
        role TEXT NULL,
        PRIMARY KEY (teacher_id, material_id),
        CONSTRAINT fk_tm_teacher
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_tm_material
            FOREIGN KEY (material_id) REFERENCES methodical_materials(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS teacher_disciplines (
        teacher_id INT NOT NULL,
        discipline_id INT NOT NULL,
        PRIMARY KEY (teacher_id, discipline_id),
        CONSTRAINT fk_td_teacher
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_td_discipline
            FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS material_associations (
        material_id INT NOT NULL,
        entity_type VARCHAR(32) NOT NULL,
        entity_id INT NOT NULL,
        PRIMARY KEY (material_id, entity_type, entity_id),
        CONSTRAINT fk_ma_material
            FOREIGN KEY (material_id) REFERENCES methodical_materials(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        version INT NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
]
