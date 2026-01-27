"""Admin controller for managing data and relationships."""
from pathlib import Path
import shutil
from typing import List, Tuple
from ..models.database import Database
from ..models.entities import (
    Teacher,
    EducationalProgram,
    Topic,
    Lesson,
    Question,
    MethodicalMaterial,
)
from ..repositories.teacher_repository import TeacherRepository
from ..repositories.program_repository import ProgramRepository
from ..repositories.topic_repository import TopicRepository
from ..repositories.lesson_repository import LessonRepository
from ..repositories.question_repository import QuestionRepository
from ..repositories.material_repository import MaterialRepository
from ..services.app_paths import get_materials_dir
from ..services.auth_service import AuthService


class AdminController:
    """Coordinates admin operations with repositories and services."""

    def __init__(self, database: Database):
        self.db = database
        self.teacher_repo = TeacherRepository(database)
        self.program_repo = ProgramRepository(database)
        self.topic_repo = TopicRepository(database)
        self.lesson_repo = LessonRepository(database)
        self.question_repo = QuestionRepository(database)
        self.material_repo = MaterialRepository(database)
        self.auth_service = AuthService()

    def verify_password(self, password: str) -> bool:
        return self.auth_service.verify_password(password)

    # Teachers
    def get_teachers(self) -> List[Teacher]:
        return self.teacher_repo.get_all()

    def add_teacher(self, teacher: Teacher) -> Teacher:
        return self.teacher_repo.add(teacher)

    def update_teacher(self, teacher: Teacher) -> Teacher:
        return self.teacher_repo.update(teacher)

    def delete_teacher(self, teacher_id: int) -> bool:
        return self.teacher_repo.delete(teacher_id)

    # Programs
    def get_programs(self) -> List[EducationalProgram]:
        return self.program_repo.get_all()

    def add_program(self, program: EducationalProgram) -> EducationalProgram:
        return self.program_repo.add(program)

    def update_program(self, program: EducationalProgram) -> EducationalProgram:
        return self.program_repo.update(program)

    def delete_program(self, program_id: int) -> bool:
        return self.program_repo.delete(program_id)

    def get_program_topics(self, program_id: int) -> List[Topic]:
        return self.program_repo.get_program_topics(program_id)

    def add_topic_to_program(self, program_id: int, topic_id: int, order_index: int = 0) -> bool:
        return self.program_repo.add_topic_to_program(program_id, topic_id, order_index)

    def remove_topic_from_program(self, program_id: int, topic_id: int) -> bool:
        return self.program_repo.remove_topic_from_program(program_id, topic_id)

    # Topics
    def get_topics(self) -> List[Topic]:
        return self.topic_repo.get_all()

    def add_topic(self, topic: Topic) -> Topic:
        return self.topic_repo.add(topic)

    def update_topic(self, topic: Topic) -> Topic:
        return self.topic_repo.update(topic)

    def delete_topic(self, topic_id: int) -> bool:
        return self.topic_repo.delete(topic_id)

    def get_topic_lessons(self, topic_id: int) -> List[Lesson]:
        return self.topic_repo.get_topic_lessons(topic_id)

    def add_lesson_to_topic(self, topic_id: int, lesson_id: int, order_index: int = 0) -> bool:
        return self.topic_repo.add_lesson_to_topic(topic_id, lesson_id, order_index)

    def remove_lesson_from_topic(self, topic_id: int, lesson_id: int) -> bool:
        return self.topic_repo.remove_lesson_from_topic(topic_id, lesson_id)

    # Lessons
    def get_lessons(self) -> List[Lesson]:
        return self.lesson_repo.get_all()

    def add_lesson(self, lesson: Lesson) -> Lesson:
        return self.lesson_repo.add(lesson)

    def update_lesson(self, lesson: Lesson) -> Lesson:
        return self.lesson_repo.update(lesson)

    def delete_lesson(self, lesson_id: int) -> bool:
        return self.lesson_repo.delete(lesson_id)

    def get_lesson_questions(self, lesson_id: int) -> List[Question]:
        return self.lesson_repo.get_lesson_questions(lesson_id)

    def add_question_to_lesson(self, lesson_id: int, question_id: int, order_index: int = 0) -> bool:
        return self.lesson_repo.add_question_to_lesson(lesson_id, question_id, order_index)

    def remove_question_from_lesson(self, lesson_id: int, question_id: int) -> bool:
        return self.lesson_repo.remove_question_from_lesson(lesson_id, question_id)

    # Questions
    def get_questions(self) -> List[Question]:
        return self.question_repo.get_all()

    def add_question(self, question: Question) -> Question:
        return self.question_repo.add(question)

    def update_question(self, question: Question) -> Question:
        return self.question_repo.update(question)

    def delete_question(self, question_id: int) -> bool:
        return self.question_repo.delete(question_id)

    # Materials
    def get_materials(self) -> List[MethodicalMaterial]:
        return self.material_repo.get_all()

    def add_material(self, material: MethodicalMaterial) -> MethodicalMaterial:
        return self.material_repo.add(material)

    def update_material(self, material: MethodicalMaterial) -> MethodicalMaterial:
        return self.material_repo.update(material)

    def delete_material(self, material_id: int) -> bool:
        return self.material_repo.delete(material_id)

    def attach_material_file(self, material: MethodicalMaterial, source_path: str) -> MethodicalMaterial:
        source = Path(source_path)
        materials_dir = get_materials_dir()
        target_name = f"material_{material.id}_{source.name}"
        target_path = materials_dir / target_name
        shutil.copy2(source, target_path)
        material.file_path = str(target_path)
        material.file_name = source.name
        return self.material_repo.update(material)

    def add_material_to_entity(self, material_id: int, entity_type: str, entity_id: int) -> bool:
        return self.material_repo.add_material_to_entity(material_id, entity_type, entity_id)

    def remove_material_from_entity(self, material_id: int, entity_type: str, entity_id: int) -> bool:
        return self.material_repo.remove_material_from_entity(material_id, entity_type, entity_id)

    def get_material_associations(self, material_id: int) -> List[Tuple[str, int, str]]:
        return self.material_repo.get_material_association_labels(material_id)

    def add_teacher_to_material(self, teacher_id: int, material_id: int, role: str = "author") -> bool:
        return self.material_repo.add_teacher_to_material(teacher_id, material_id, role)

    def remove_teacher_from_material(self, teacher_id: int, material_id: int) -> bool:
        return self.material_repo.remove_teacher_from_material(teacher_id, material_id)
