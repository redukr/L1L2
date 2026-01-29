"""Admin controller for managing data and relationships."""
from typing import List, Tuple
from ..models.database import Database
from ..models.entities import (
    Teacher,
    EducationalProgram,
    Discipline,
    Topic,
    Lesson,
    LessonType,
    MaterialType,
    Question,
    MethodicalMaterial,
)
from ..repositories.teacher_repository import TeacherRepository
from ..repositories.program_repository import ProgramRepository
from ..repositories.discipline_repository import DisciplineRepository
from ..repositories.topic_repository import TopicRepository
from ..repositories.lesson_repository import LessonRepository
from ..repositories.lesson_type_repository import LessonTypeRepository
from ..repositories.question_repository import QuestionRepository
from ..repositories.material_repository import MaterialRepository
from ..repositories.material_type_repository import MaterialTypeRepository
from ..services.file_storage import FileStorageManager
from ..services.auth_service import AuthService


class AdminController:
    """Coordinates admin operations with repositories and services."""

    def __init__(self, database: Database):
        self.db = database
        self.teacher_repo = TeacherRepository(database)
        self.program_repo = ProgramRepository(database)
        self.discipline_repo = DisciplineRepository(database)
        self.topic_repo = TopicRepository(database)
        self.lesson_repo = LessonRepository(database)
        self.lesson_type_repo = LessonTypeRepository(database)
        self.question_repo = QuestionRepository(database)
        self.material_repo = MaterialRepository(database)
        self.material_type_repo = MaterialTypeRepository(database)
        self.file_storage = FileStorageManager()
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

    def get_program_disciplines(self, program_id: int) -> List[Discipline]:
        return self.program_repo.get_program_disciplines(program_id)

    def add_discipline_to_program(self, program_id: int, discipline_id: int, order_index: int = 0) -> bool:
        return self.program_repo.add_discipline_to_program(program_id, discipline_id, order_index)

    def remove_discipline_from_program(self, program_id: int, discipline_id: int) -> bool:
        return self.program_repo.remove_discipline_from_program(program_id, discipline_id)

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

    # Disciplines
    def get_disciplines(self) -> List[Discipline]:
        return self.discipline_repo.get_all()

    def add_discipline(self, discipline: Discipline) -> Discipline:
        return self.discipline_repo.add(discipline)

    def update_discipline(self, discipline: Discipline) -> Discipline:
        return self.discipline_repo.update(discipline)

    def delete_discipline(self, discipline_id: int) -> bool:
        return self.discipline_repo.delete(discipline_id)

    def get_discipline_topics(self, discipline_id: int) -> List[Topic]:
        return self.discipline_repo.get_discipline_topics(discipline_id)

    def add_topic_to_discipline(self, discipline_id: int, topic_id: int, order_index: int = 0) -> bool:
        return self.discipline_repo.add_topic_to_discipline(discipline_id, topic_id, order_index)

    def remove_topic_from_discipline(self, discipline_id: int, topic_id: int) -> bool:
        return self.discipline_repo.remove_topic_from_discipline(discipline_id, topic_id)

    # Lessons
    def get_lessons(self) -> List[Lesson]:
        return self.lesson_repo.get_all()

    def add_lesson(self, lesson: Lesson) -> Lesson:
        return self.lesson_repo.add(lesson)

    def update_lesson(self, lesson: Lesson) -> Lesson:
        return self.lesson_repo.update(lesson)

    def delete_lesson(self, lesson_id: int) -> bool:
        return self.lesson_repo.delete(lesson_id)

    # Lesson types
    def get_lesson_types(self) -> List[LessonType]:
        return self.lesson_type_repo.get_all()

    def add_lesson_type(self, lesson_type: LessonType) -> LessonType:
        return self.lesson_type_repo.add(lesson_type)

    def update_lesson_type(self, lesson_type: LessonType) -> LessonType:
        return self.lesson_type_repo.update(lesson_type)

    def delete_lesson_type(self, lesson_type_id: int) -> bool:
        return self.lesson_type_repo.delete(lesson_type_id)

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

    def get_materials_for_entity(self, entity_type: str, entity_id: int) -> List[MethodicalMaterial]:
        return self.material_repo.get_materials_for_entity(entity_type, entity_id)

    def add_material(self, material: MethodicalMaterial) -> MethodicalMaterial:
        return self.material_repo.add(material)

    def update_material(self, material: MethodicalMaterial) -> MethodicalMaterial:
        return self.material_repo.update(material)

    def delete_material(self, material_id: int) -> bool:
        material = self.material_repo.get_by_id(material_id)
        if material and material.relative_path:
            self.file_storage.delete_file(material.relative_path)
        return self.material_repo.delete(material_id)

    # Material types
    def get_material_types(self) -> List[MaterialType]:
        return self.material_type_repo.get_all()

    def add_material_type(self, material_type: MaterialType) -> MaterialType:
        return self.material_type_repo.add(material_type)

    def update_material_type(self, material_type: MaterialType) -> MaterialType:
        return self.material_type_repo.update(material_type)

    def delete_material_type(self, material_type_id: int) -> bool:
        return self.material_type_repo.delete(material_type_id)

    def attach_material_file(self, material: MethodicalMaterial, source_path: str) -> MethodicalMaterial:
        associations = self.material_repo.get_material_associations(material.id)
        if not associations:
            raise ValueError("Material must be linked to a program/discipline/topic/lesson before attaching a file.")
        program_id, discipline_id = self._resolve_program_discipline(associations)
        return self.attach_material_file_with_context(material, source_path, program_id, discipline_id)

    def attach_material_file_with_context(
        self, material: MethodicalMaterial, source_path: str, program_id: int, discipline_id: int
    ) -> MethodicalMaterial:
        original_filename, stored_filename, relative_path, file_type = self.file_storage.store_material_file(
            source_path, program_id, discipline_id, material.id
        )
        if material.relative_path and material.relative_path != relative_path:
            self.file_storage.delete_file(material.relative_path)
        material.original_filename = original_filename
        material.stored_filename = stored_filename
        material.relative_path = relative_path
        material.file_type = file_type
        material.file_name = original_filename
        material.file_path = relative_path
        try:
            return self.material_repo.update(material)
        except Exception:
            self.file_storage.delete_file(relative_path)
            raise

    def attach_existing_material_file(self, material: MethodicalMaterial, source_path: str) -> MethodicalMaterial:
        original_filename, stored_filename, relative_path, file_type = self.file_storage.attach_existing_file(
            source_path
        )
        if material.relative_path and material.relative_path != relative_path:
            self.file_storage.delete_file(material.relative_path)
        material.original_filename = original_filename
        material.stored_filename = stored_filename
        material.relative_path = relative_path
        material.file_type = file_type
        material.file_name = original_filename
        material.file_path = relative_path
        return self.material_repo.update(material)

    def _resolve_program_discipline(self, associations: List[Tuple[str, int]]) -> Tuple[int, int]:
        entity_type, entity_id = associations[0]
        if entity_type == "program":
            programs = self.program_repo.get_by_id(entity_id)
            if not programs:
                raise ValueError("Program association not found.")
            disciplines = self.program_repo.get_program_disciplines(entity_id)
            if not disciplines:
                raise ValueError("Program has no disciplines.")
            return entity_id, disciplines[0].id
        if entity_type == "discipline":
            programs = self.program_repo.get_programs_for_discipline(entity_id)
            if not programs:
                raise ValueError("Discipline is not linked to any program.")
            return programs[0].id, entity_id
        if entity_type == "topic":
            programs = self.program_repo.get_programs_for_topic(entity_id)
            disciplines = self.discipline_repo.get_disciplines_for_topic(entity_id)
            if not programs or not disciplines:
                raise ValueError("Topic is not linked to program/discipline.")
            return programs[0].id, disciplines[0].id
        if entity_type == "lesson":
            programs = self.program_repo.get_programs_for_lesson(entity_id)
            disciplines = self.discipline_repo.get_disciplines_for_lesson(entity_id)
            if not programs or not disciplines:
                topics = self.topic_repo.get_topics_for_lesson(entity_id)
                if topics:
                    disciplines = self.discipline_repo.get_disciplines_for_topic(topics[0].id)
                    if disciplines:
                        programs = self.program_repo.get_programs_for_discipline(disciplines[0].id)
            if not programs or not disciplines:
                raise ValueError("Lesson is not linked to program/discipline.")
            return programs[0].id, disciplines[0].id
        raise ValueError("Unsupported material association.")

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
