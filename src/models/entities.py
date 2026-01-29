"""Data entities for the educational program management application."""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Teacher:
    """Represents a teacher in the system."""
    id: Optional[int] = None
    full_name: str = ""
    military_rank: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class EducationalProgram:
    """Represents an educational program."""
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    level: Optional[str] = None
    duration_hours: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    disciplines: List['Discipline'] = field(default_factory=list)


@dataclass
class Topic:
    """Represents a topic within an educational program."""
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    order_index: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    lessons: List['Lesson'] = field(default_factory=list)


@dataclass
class Lesson:
    """Represents a lesson within a topic."""
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    duration_hours: float = 1.0
    lesson_type_id: Optional[int] = None
    lesson_type_name: Optional[str] = None
    classroom_hours: Optional[float] = None
    self_study_hours: Optional[float] = None
    order_index: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    questions: List['Question'] = field(default_factory=list)


@dataclass
class Question:
    """Represents a question within a lesson."""
    id: Optional[int] = None
    content: str = ""
    answer: Optional[str] = None
    difficulty_level: int = 1
    order_index: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class MethodicalMaterial:
    """Represents methodical material associated with an entity."""
    id: Optional[int] = None
    title: str = ""
    material_type: str = "guide"  # plan, guide, presentation, attachment
    description: Optional[str] = None
    original_filename: Optional[str] = None
    stored_filename: Optional[str] = None
    relative_path: Optional[str] = None
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    teachers: List[Teacher] = field(default_factory=list)


@dataclass
class SearchResult:
    """Represents a search result with context."""
    entity_type: str  # 'teacher', 'program', 'topic', 'lesson', 'question', 'material'
    entity_id: int
    title: str
    description: str
    matched_text: str
    relevance_score: float = 0.0
@dataclass
class Discipline:
    """Represents a discipline within an educational program."""
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    order_index: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    topics: List['Topic'] = field(default_factory=list)


@dataclass
class LessonType:
    """Represents a lesson type."""
    id: Optional[int] = None
    name: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class MaterialType:
    """Represents a material type."""
    id: Optional[int] = None
    name: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
