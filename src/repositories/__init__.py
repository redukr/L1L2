"""Repositories package for data access layer."""
from .teacher_repository import TeacherRepository
from .program_repository import ProgramRepository
from .topic_repository import TopicRepository
from .lesson_repository import LessonRepository
from .question_repository import QuestionRepository
from .material_repository import MaterialRepository

__all__ = [
    'TeacherRepository',
    'ProgramRepository',
    'TopicRepository',
    'LessonRepository',
    'QuestionRepository',
    'MaterialRepository',
]
