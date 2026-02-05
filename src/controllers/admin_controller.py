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

    def get_teacher_disciplines(self, teacher_id: int):
        return self.teacher_repo.get_disciplines(teacher_id)

    def add_discipline_to_teacher(self, teacher_id: int, discipline_id: int) -> bool:
        return self.teacher_repo.add_discipline(teacher_id, discipline_id)

    def remove_discipline_from_teacher(self, teacher_id: int, discipline_id: int) -> bool:
        return self.teacher_repo.remove_discipline(teacher_id, discipline_id)

    def get_teachers_for_disciplines(self, discipline_ids: List[int]) -> List[Teacher]:
        return self.teacher_repo.get_teachers_for_disciplines(discipline_ids)

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

    def update_topic_lesson_order(self, topic_id: int, lesson_id: int, order_index: int) -> bool:
        return self.topic_repo.update_lesson_order(topic_id, lesson_id, order_index)

    def normalize_topic_lesson_order(self, topic_id: int) -> None:
        lessons = self.topic_repo.get_topic_lessons(topic_id)
        if not lessons:
            return
        def sort_key(lesson: Lesson) -> tuple:
            order = lesson.order_index if lesson.order_index and lesson.order_index > 0 else 10**9
            return (order, lesson.title or "")
        ordered = sorted(lessons, key=sort_key)
        for idx, lesson in enumerate(ordered, start=1):
            self.topic_repo.update_lesson_order(topic_id, lesson.id, idx)

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

    def get_primary_parent_ids(self, entity_type: str, entity_id: int) -> Tuple[int | None, int | None]:
        return self._resolve_program_discipline_for_entity(entity_type, entity_id)

    def move_discipline_to_program(self, discipline_id: int, from_program_id: int, to_program_id: int) -> None:
        if not from_program_id or not to_program_id or from_program_id == to_program_id:
            return
        self.program_repo.remove_discipline_from_program(from_program_id, discipline_id)
        order_index = self._get_next_order_index("program_disciplines", "program_id", to_program_id)
        self.program_repo.add_discipline_to_program(to_program_id, discipline_id, order_index)

    def move_topic_to_discipline(self, topic_id: int, from_discipline_id: int, to_discipline_id: int) -> None:
        if not from_discipline_id or not to_discipline_id or from_discipline_id == to_discipline_id:
            return
        self.discipline_repo.remove_topic_from_discipline(from_discipline_id, topic_id)
        order_index = self._get_next_order_index("discipline_topics", "discipline_id", to_discipline_id)
        self.discipline_repo.add_topic_to_discipline(to_discipline_id, topic_id, order_index)

    def convert_discipline_to_topic(
        self, discipline: Discipline, from_program_id: int, to_discipline_id: int
    ) -> Topic:
        if not to_discipline_id:
            raise ValueError("Target discipline is required.")
        if discipline.id == to_discipline_id:
            raise ValueError("Discipline cannot be converted under itself.")
        new_topic = Topic(
            title=discipline.name,
            description=discipline.description,
            order_index=discipline.order_index,
        )
        new_topic = self.topic_repo.add(new_topic)
        order_index = self._get_next_order_index("discipline_topics", "discipline_id", to_discipline_id)
        self.discipline_repo.add_topic_to_discipline(to_discipline_id, new_topic.id, order_index)

        for material in self.material_repo.get_materials_for_entity("discipline", discipline.id):
            self.material_repo.add_material_to_entity(material.id, "topic", new_topic.id)
            self.material_repo.remove_material_from_entity(material.id, "discipline", discipline.id)

        for topic in self.discipline_repo.get_discipline_topics(discipline.id):
            self.discipline_repo.remove_topic_from_discipline(discipline.id, topic.id)
            self.discipline_repo.add_topic_to_discipline(to_discipline_id, topic.id, topic.order_index)

        if from_program_id:
            self.program_repo.remove_discipline_from_program(from_program_id, discipline.id)
        if not self.program_repo.get_programs_for_discipline(discipline.id):
            self.discipline_repo.delete(discipline.id)
        return new_topic

    def convert_topic_to_discipline(
        self, topic: Topic, from_discipline_id: int, to_program_id: int
    ) -> Discipline:
        if not to_program_id:
            raise ValueError("Target program is required.")
        new_discipline = Discipline(
            name=topic.title,
            description=topic.description,
            order_index=topic.order_index,
        )
        new_discipline = self.discipline_repo.add(new_discipline)
        order_index = self._get_next_order_index("program_disciplines", "program_id", to_program_id)
        self.program_repo.add_discipline_to_program(to_program_id, new_discipline.id, order_index)

        new_topic = Topic(
            title=topic.title,
            description=topic.description,
            order_index=1,
        )
        new_topic = self.topic_repo.add(new_topic)
        self.discipline_repo.add_topic_to_discipline(new_discipline.id, new_topic.id, 1)

        for lesson, order in self._get_topic_lessons_with_order(topic.id):
            self.topic_repo.remove_lesson_from_topic(topic.id, lesson.id)
            self.topic_repo.add_lesson_to_topic(new_topic.id, lesson.id, order or lesson.order_index)

        for material in self.material_repo.get_materials_for_entity("topic", topic.id):
            self.material_repo.add_material_to_entity(material.id, "discipline", new_discipline.id)
            self.material_repo.remove_material_from_entity(material.id, "topic", topic.id)

        if from_discipline_id:
            self.discipline_repo.remove_topic_from_discipline(from_discipline_id, topic.id)
        if not self.discipline_repo.get_disciplines_for_topic(topic.id) and not self.program_repo.get_programs_for_topic(topic.id):
            self.topic_repo.delete(topic.id)
        return new_discipline

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

    def update_lesson_question_order(self, lesson_id: int, question_id: int, order_index: int) -> bool:
        return self.lesson_repo.update_question_order(lesson_id, question_id, order_index)

    def get_next_lesson_question_order(self, lesson_id: int) -> int:
        return self.lesson_repo.get_next_question_order(lesson_id)

    def normalize_lesson_question_order(self, lesson_id: int) -> None:
        self.lesson_repo.normalize_question_order(lesson_id)

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
        existing = self.material_type_repo.get_by_id(material_type.id) if material_type.id else None
        updated = self.material_type_repo.update(material_type)
        if existing and existing.name != updated.name:
            self.material_repo.update_material_type_name(existing.name, updated.name)
        return updated

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

    def duplicate_program(self, program_id: int) -> EducationalProgram:
        program = self.program_repo.get_by_id(program_id)
        if not program:
            raise ValueError("Program not found.")
        new_program = EducationalProgram(
            name=self._copy_name(program.name),
            description=program.description,
            level=program.level,
            year=program.year,
            duration_hours=program.duration_hours,
        )
        new_program = self.program_repo.add(new_program)
        for discipline in self.program_repo.get_program_disciplines(program_id):
            order_index = self._get_next_order_index("program_disciplines", "program_id", new_program.id)
            self.program_repo.add_discipline_to_program(new_program.id, discipline.id, order_index)
        for material in self.material_repo.get_materials_for_entity("program", program_id):
            self.material_repo.add_material_to_entity(material.id, "program", new_program.id)
        return new_program

    def copy_program(self, program_id: int) -> EducationalProgram:
        program = self.program_repo.get_by_id(program_id)
        if not program:
            raise ValueError("Program not found.")
        new_program = EducationalProgram(
            name=self._copy_name(program.name),
            description=program.description,
            level=program.level,
            year=program.year,
            duration_hours=program.duration_hours,
        )
        new_program = self.program_repo.add(new_program)
        material_map: dict[int, MethodicalMaterial] = {}
        discipline_map: dict[int, Discipline] = {}
        for discipline in self.program_repo.get_program_disciplines(program_id):
            new_discipline = self._copy_discipline_tree(
                discipline, new_program.id, material_map, discipline.order_index
            )
            discipline_map[discipline.id] = new_discipline
        for material in self.material_repo.get_materials_for_entity("program", program_id):
            discipline_id = next(iter(discipline_map.values())).id if discipline_map else None
            if discipline_id is None:
                continue
            new_material = self._copy_material(material, new_program.id, discipline_id, material_map)
            self.material_repo.add_material_to_entity(new_material.id, "program", new_program.id)
        return new_program

    def duplicate_discipline(self, discipline_id: int, program_id: int) -> Discipline:
        discipline = self.discipline_repo.get_by_id(discipline_id)
        if not discipline:
            raise ValueError("Discipline not found.")
        new_discipline = self._clone_discipline_links(discipline_id, rename=True)
        order_index = self._get_next_order_index("program_disciplines", "program_id", program_id)
        self.program_repo.add_discipline_to_program(program_id, new_discipline.id, order_index)
        return new_discipline

    def copy_discipline(self, discipline_id: int, program_id: int) -> Discipline:
        discipline = self.discipline_repo.get_by_id(discipline_id)
        if not discipline:
            raise ValueError("Discipline not found.")
        material_map: dict[int, MethodicalMaterial] = {}
        return self._copy_discipline_tree(discipline, program_id, material_map)

    def duplicate_topic(self, topic_id: int, discipline_id: int) -> Topic:
        new_topic = self._clone_topic_links(topic_id, rename=True)
        order_index = self._get_next_order_index("discipline_topics", "discipline_id", discipline_id)
        self.discipline_repo.add_topic_to_discipline(discipline_id, new_topic.id, order_index)
        return new_topic

    def copy_topic(self, topic_id: int, discipline_id: int) -> Topic:
        material_map: dict[int, MethodicalMaterial] = {}
        topic = self.topic_repo.get_by_id(topic_id)
        if not topic:
            raise ValueError("Topic not found.")
        program_id, _ = self._resolve_program_discipline_for_entity("discipline", discipline_id)
        return self._copy_topic_tree(topic, program_id, discipline_id, material_map)

    def duplicate_lesson(self, lesson_id: int, topic_id: int) -> Lesson:
        new_lesson = self._clone_lesson_links(lesson_id, rename=True)
        order_index = self._get_next_order_index("topic_lessons", "topic_id", topic_id)
        self.topic_repo.add_lesson_to_topic(topic_id, new_lesson.id, order_index)
        return new_lesson

    def copy_lesson(self, lesson_id: int, topic_id: int) -> Lesson:
        material_map: dict[int, MethodicalMaterial] = {}
        lesson = self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise ValueError("Lesson not found.")
        program_id, discipline_id = self._resolve_program_discipline_for_entity("topic", topic_id)
        return self._copy_lesson_tree(lesson, topic_id, program_id, discipline_id, material_map)

    def duplicate_question(self, question_id: int, lesson_id: int) -> Question:
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise ValueError("Question not found.")
        new_question = Question(
            content=question.content,
            answer=question.answer,
            order_index=question.order_index,
        )
        new_question = self.question_repo.add(new_question)
        order_index = self._get_next_order_index("lesson_questions", "lesson_id", lesson_id)
        self.lesson_repo.add_question_to_lesson(lesson_id, new_question.id, order_index)
        return new_question

    def copy_question(self, question_id: int, lesson_id: int) -> Question:
        return self.duplicate_question(question_id, lesson_id)

    def ensure_discipline_for_edit(self, discipline_id: int, program_id: int) -> Discipline:
        if not self._is_shared("program_disciplines", "discipline_id", discipline_id):
            return self.discipline_repo.get_by_id(discipline_id)
        order_index = self._get_assoc_order_index(
            "program_disciplines", "program_id", "discipline_id", program_id, discipline_id
        )
        new_discipline = self._clone_discipline_links(discipline_id, rename=False)
        self._replace_assoc(
            "program_disciplines", "program_id", "discipline_id", program_id, discipline_id, new_discipline.id, order_index
        )
        return new_discipline

    def ensure_topic_for_edit(self, topic_id: int, discipline_id: int) -> Topic:
        if not self._is_shared("discipline_topics", "topic_id", topic_id):
            return self.topic_repo.get_by_id(topic_id)
        order_index = self._get_assoc_order_index(
            "discipline_topics", "discipline_id", "topic_id", discipline_id, topic_id
        )
        new_topic = self._clone_topic_links(topic_id, rename=False)
        self._replace_assoc(
            "discipline_topics", "discipline_id", "topic_id", discipline_id, topic_id, new_topic.id, order_index
        )
        return new_topic

    def ensure_lesson_for_edit(self, lesson_id: int, topic_id: int) -> Lesson:
        if not self._is_shared("topic_lessons", "lesson_id", lesson_id):
            return self.lesson_repo.get_by_id(lesson_id)
        order_index = self._get_assoc_order_index(
            "topic_lessons", "topic_id", "lesson_id", topic_id, lesson_id
        )
        new_lesson = self._clone_lesson_links(lesson_id, rename=False)
        self._replace_assoc(
            "topic_lessons", "topic_id", "lesson_id", topic_id, lesson_id, new_lesson.id, order_index
        )
        return new_lesson

    def ensure_question_for_edit(self, question_id: int, lesson_id: int) -> Question:
        if not self._is_shared("lesson_questions", "question_id", question_id):
            return self.question_repo.get_by_id(question_id)
        order_index = self._get_assoc_order_index(
            "lesson_questions", "lesson_id", "question_id", lesson_id, question_id
        )
        question = self.question_repo.get_by_id(question_id)
        new_question = Question(
            content=question.content,
            answer=question.answer,
            order_index=question.order_index,
        )
        new_question = self.question_repo.add(new_question)
        self._replace_assoc(
            "lesson_questions", "lesson_id", "question_id", lesson_id, question_id, new_question.id, order_index
        )
        return new_question

    def ensure_material_for_edit(self, material: MethodicalMaterial, entity_type: str, entity_id: int) -> MethodicalMaterial:
        associations = self.material_repo.get_material_associations(material.id)
        if len(associations) <= 1:
            return material
        program_id, discipline_id = self._resolve_program_discipline_for_entity(entity_type, entity_id)
        new_material = MethodicalMaterial(
            title=material.title,
            material_type=material.material_type,
            description=material.description,
        )
        new_material = self.material_repo.add(new_material)
        teachers = self.material_repo.get_material_teachers(material.id)
        for teacher in teachers:
            self.material_repo.add_teacher_to_material(teacher.id, new_material.id)
        new_material.teachers = teachers
        if material.relative_path and program_id and discipline_id:
            source_path = str(self.file_storage._resolve_path(material.relative_path))
            new_material = self.attach_material_file_with_context(new_material, source_path, program_id, discipline_id)
        self.material_repo.add_material_to_entity(new_material.id, entity_type, entity_id)
        self.material_repo.remove_material_from_entity(material.id, entity_type, entity_id)
        return new_material

    def _copy_discipline_tree(
        self,
        discipline: Discipline,
        program_id: int,
        material_map: dict[int, MethodicalMaterial],
        order_index: int | None = None,
    ) -> Discipline:
        new_discipline = Discipline(
            name=self._copy_name(discipline.name),
            description=discipline.description,
            order_index=discipline.order_index,
        )
        new_discipline = self.discipline_repo.add(new_discipline)
        order_index = order_index if order_index is not None else self._get_next_order_index(
            "program_disciplines", "program_id", program_id
        )
        self.program_repo.add_discipline_to_program(program_id, new_discipline.id, order_index)
        for teacher in self.teacher_repo.get_teachers_for_disciplines([discipline.id]):
            self.teacher_repo.add_discipline(teacher.id, new_discipline.id)
        for topic in self.discipline_repo.get_discipline_topics(discipline.id):
            self._copy_topic_tree(topic, program_id, new_discipline.id, material_map, topic.order_index)
        for material in self.material_repo.get_materials_for_entity("discipline", discipline.id):
            new_material = self._copy_material(material, program_id, new_discipline.id, material_map)
            self.material_repo.add_material_to_entity(new_material.id, "discipline", new_discipline.id)
        return new_discipline

    def _copy_topic_tree(
        self,
        topic: Topic,
        program_id: int,
        discipline_id: int,
        material_map: dict[int, MethodicalMaterial],
        order_index: int | None = None,
    ) -> Topic:
        new_topic = Topic(
            title=self._copy_name(topic.title),
            description=topic.description,
            order_index=topic.order_index,
        )
        new_topic = self.topic_repo.add(new_topic)
        order_index = order_index if order_index is not None else self._get_next_order_index(
            "discipline_topics", "discipline_id", discipline_id
        )
        self.discipline_repo.add_topic_to_discipline(discipline_id, new_topic.id, order_index)
        for lesson, order in self._get_topic_lessons_with_order(topic.id):
            self._copy_lesson_tree(lesson, new_topic.id, program_id, discipline_id, material_map, order)
        for material in self.material_repo.get_materials_for_entity("topic", topic.id):
            new_material = self._copy_material(material, program_id, discipline_id, material_map)
            self.material_repo.add_material_to_entity(new_material.id, "topic", new_topic.id)
        return new_topic

    def _copy_lesson_tree(
        self,
        lesson: Lesson,
        topic_id: int,
        program_id: int,
        discipline_id: int,
        material_map: dict[int, MethodicalMaterial],
        order_index: int | None = None,
    ) -> Lesson:
        new_lesson = Lesson(
            title=self._copy_name(lesson.title),
            description=lesson.description,
            duration_hours=lesson.duration_hours,
            lesson_type_id=lesson.lesson_type_id,
            classroom_hours=lesson.classroom_hours,
            self_study_hours=lesson.self_study_hours,
            order_index=lesson.order_index,
        )
        new_lesson = self.lesson_repo.add(new_lesson)
        order_index = order_index if order_index is not None else self._get_next_order_index("topic_lessons", "topic_id", topic_id)
        self.topic_repo.add_lesson_to_topic(topic_id, new_lesson.id, order_index)
        for question, q_order in self._get_lesson_questions_with_order(lesson.id):
            new_question = Question(
                content=question.content,
                answer=question.answer,
                order_index=question.order_index,
            )
            new_question = self.question_repo.add(new_question)
            self.lesson_repo.add_question_to_lesson(new_lesson.id, new_question.id, q_order)
        for material in self.material_repo.get_materials_for_entity("lesson", lesson.id):
            new_material = self._copy_material(material, program_id, discipline_id, material_map)
            self.material_repo.add_material_to_entity(new_material.id, "lesson", new_lesson.id)
        return new_lesson

    def _copy_material(
        self,
        material: MethodicalMaterial,
        program_id: int,
        discipline_id: int,
        material_map: dict[int, MethodicalMaterial],
    ) -> MethodicalMaterial:
        if material.id in material_map:
            return material_map[material.id]
        new_material = MethodicalMaterial(
            title=material.title,
            material_type=material.material_type,
            description=material.description,
        )
        new_material = self.material_repo.add(new_material)
        for teacher in self.material_repo.get_material_teachers(material.id):
            self.material_repo.add_teacher_to_material(teacher.id, new_material.id)
        if material.relative_path and program_id and discipline_id:
            source_path = str(self.file_storage._resolve_path(material.relative_path))
            self.attach_material_file_with_context(new_material, source_path, program_id, discipline_id)
        material_map[material.id] = new_material
        return new_material

    def _clone_discipline_links(self, discipline_id: int, rename: bool = True) -> Discipline:
        discipline = self.discipline_repo.get_by_id(discipline_id)
        name = self._copy_name(discipline.name) if rename else discipline.name
        new_discipline = Discipline(
            name=name,
            description=discipline.description,
            order_index=discipline.order_index,
        )
        new_discipline = self.discipline_repo.add(new_discipline)
        for discipline_topic in self.discipline_repo.get_discipline_topics(discipline_id):
            self.discipline_repo.add_topic_to_discipline(
                new_discipline.id, discipline_topic.id, discipline_topic.order_index
            )
        for material in self.material_repo.get_materials_for_entity("discipline", discipline_id):
            self.material_repo.add_material_to_entity(material.id, "discipline", new_discipline.id)
        for teacher in self.teacher_repo.get_teachers_for_disciplines([discipline_id]):
            self.teacher_repo.add_discipline(teacher.id, new_discipline.id)
        return new_discipline

    def _clone_topic_links(self, topic_id: int, rename: bool = True) -> Topic:
        topic = self.topic_repo.get_by_id(topic_id)
        title = self._copy_name(topic.title) if rename else topic.title
        new_topic = Topic(
            title=title,
            description=topic.description,
            order_index=topic.order_index,
        )
        new_topic = self.topic_repo.add(new_topic)
        for lesson, order in self._get_topic_lessons_with_order(topic_id):
            self.topic_repo.add_lesson_to_topic(new_topic.id, lesson.id, order)
        for material in self.material_repo.get_materials_for_entity("topic", topic_id):
            self.material_repo.add_material_to_entity(material.id, "topic", new_topic.id)
        return new_topic

    def _clone_lesson_links(self, lesson_id: int, rename: bool = True) -> Lesson:
        lesson = self.lesson_repo.get_by_id(lesson_id)
        title = self._copy_name(lesson.title) if rename else lesson.title
        new_lesson = Lesson(
            title=title,
            description=lesson.description,
            duration_hours=lesson.duration_hours,
            lesson_type_id=lesson.lesson_type_id,
            classroom_hours=lesson.classroom_hours,
            self_study_hours=lesson.self_study_hours,
            order_index=lesson.order_index,
        )
        new_lesson = self.lesson_repo.add(new_lesson)
        for question, q_order in self._get_lesson_questions_with_order(lesson_id):
            self.lesson_repo.add_question_to_lesson(new_lesson.id, question.id, q_order)
        for material in self.material_repo.get_materials_for_entity("lesson", lesson_id):
            self.material_repo.add_material_to_entity(material.id, "lesson", new_lesson.id)
        return new_lesson

    def _get_topic_lessons_with_order(self, topic_id: int) -> List[Tuple[Lesson, int]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id, l.title, l.description, l.duration_hours,
                       l.lesson_type_id, l.classroom_hours, l.self_study_hours,
                       l.order_index, l.created_at, l.updated_at,
                       tl.order_index as link_order
                FROM lessons l
                JOIN topic_lessons tl ON l.id = tl.lesson_id
                WHERE tl.topic_id = ?
                ORDER BY tl.order_index
            """, (topic_id,))
            lessons = []
            for row in cursor.fetchall():
                lesson = self.lesson_repo._row_to_lesson(row)
                lessons.append((lesson, row["link_order"]))
            return lessons

    def _get_lesson_questions_with_order(self, lesson_id: int) -> List[Tuple[Question, int]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.id, q.content, q.answer,
                       q.order_index, q.created_at, q.updated_at,
                       lq.order_index as link_order
                FROM questions q
                JOIN lesson_questions lq ON q.id = lq.question_id
                WHERE lq.lesson_id = ?
                ORDER BY CASE
                    WHEN lq.order_index IS NULL OR lq.order_index = 0 THEN q.order_index
                    ELSE lq.order_index
                END, q.order_index
            """, (lesson_id,))
            questions = []
            for row in cursor.fetchall():
                question = self.question_repo._row_to_question(row)
                questions.append((question, row["link_order"]))
            return questions

    def _resolve_program_discipline_for_entity(self, entity_type: str, entity_id: int) -> Tuple[int | None, int | None]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if entity_type == "discipline":
                cursor.execute("""
                    SELECT program_id FROM program_disciplines
                    WHERE discipline_id = ?
                    ORDER BY program_id
                    LIMIT 1
                """, (entity_id,))
                row = cursor.fetchone()
                return (row["program_id"], entity_id) if row else (None, None)
            if entity_type == "lesson":
                cursor.execute("""
                    SELECT dt.discipline_id, pd.program_id
                    FROM topic_lessons tl
                    JOIN discipline_topics dt ON tl.topic_id = dt.topic_id
                    JOIN program_disciplines pd ON dt.discipline_id = pd.discipline_id
                    WHERE tl.lesson_id = ?
                    LIMIT 1
                """, (entity_id,))
                row = cursor.fetchone()
                return (row["program_id"], row["discipline_id"]) if row else (None, None)
            if entity_type == "program":
                cursor.execute("""
                    SELECT discipline_id
                    FROM program_disciplines
                    WHERE program_id = ?
                    ORDER BY order_index
                    LIMIT 1
                """, (entity_id,))
                row = cursor.fetchone()
                return (entity_id, row["discipline_id"]) if row else (None, None)
            if entity_type == "topic":
                cursor.execute("""
                    SELECT dt.discipline_id, pd.program_id
                    FROM discipline_topics dt
                    JOIN program_disciplines pd ON dt.discipline_id = pd.discipline_id
                    WHERE dt.topic_id = ?
                    LIMIT 1
                """, (entity_id,))
                row = cursor.fetchone()
                return (row["program_id"], row["discipline_id"]) if row else (None, None)
        return None, None

    def _is_shared(self, table: str, child_column: str, child_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {table} WHERE {child_column} = ?", (child_id,))
            row = cursor.fetchone()
            return row["cnt"] > 1

    def _get_assoc_order_index(
        self, table: str, parent_column: str, child_column: str, parent_id: int, child_id: int
    ) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT order_index FROM {table} WHERE {parent_column} = ? AND {child_column} = ?",
                (parent_id, child_id),
            )
            row = cursor.fetchone()
            return row["order_index"] if row else 0

    def _get_next_order_index(self, table: str, parent_column: str, parent_id: int) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT COALESCE(MAX(order_index), 0) + 1 as next_idx FROM {table} WHERE {parent_column} = ?",
                (parent_id,),
            )
            row = cursor.fetchone()
            return row["next_idx"] if row else 1

    def _replace_assoc(
        self,
        table: str,
        parent_column: str,
        child_column: str,
        parent_id: int,
        old_child_id: int,
        new_child_id: int,
        order_index: int,
    ) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {table} WHERE {parent_column} = ? AND {child_column} = ?",
                (parent_id, old_child_id),
            )
            cursor.execute(
                f"INSERT INTO {table} ({parent_column}, {child_column}, order_index) VALUES (?, ?, ?)",
                (parent_id, new_child_id, order_index),
            )

    def _copy_name(self, base: str) -> str:
        base = base or "Copy"
        candidate = f"{base} (copy)"
        return candidate
    def check_database(self) -> str:
        with self.db.get_connection() as conn:
            rows = conn.execute("PRAGMA integrity_check;").fetchall()
        return ", ".join(row[0] for row in rows)

    def get_unused_data_counts(self) -> dict:
        with self.db.get_connection() as conn:
            program_count = conn.execute(
                """
                SELECT COUNT(*) FROM educational_programs p
                WHERE NOT EXISTS (
                    SELECT 1 FROM program_disciplines pd WHERE pd.program_id = p.id
                )
                AND NOT EXISTS (
                    SELECT 1 FROM program_topics pt WHERE pt.program_id = p.id
                )
                """
            ).fetchone()[0]
            discipline_count = conn.execute(
                """
                SELECT COUNT(*) FROM disciplines d
                WHERE NOT EXISTS (
                    SELECT 1 FROM program_disciplines pd WHERE pd.discipline_id = d.id
                )
                """
            ).fetchone()[0]
            topic_count = conn.execute(
                """
                SELECT COUNT(*) FROM topics t
                WHERE NOT EXISTS (
                    SELECT 1 FROM discipline_topics dt WHERE dt.topic_id = t.id
                )
                AND NOT EXISTS (
                    SELECT 1 FROM program_topics pt WHERE pt.topic_id = t.id
                )
                """
            ).fetchone()[0]
            lesson_count = conn.execute(
                """
                SELECT COUNT(*) FROM lessons l
                WHERE NOT EXISTS (
                    SELECT 1 FROM topic_lessons tl WHERE tl.lesson_id = l.id
                )
                """
            ).fetchone()[0]
            question_count = conn.execute(
                """
                SELECT COUNT(*) FROM questions q
                WHERE NOT EXISTS (
                    SELECT 1 FROM lesson_questions lq WHERE lq.question_id = q.id
                )
                """
            ).fetchone()[0]
            material_count = conn.execute(
                """
                SELECT COUNT(*) FROM methodical_materials m
                WHERE NOT EXISTS (
                    SELECT 1 FROM material_associations ma WHERE ma.material_id = m.id
                )
                """
            ).fetchone()[0]
        return {
            "programs": program_count,
            "disciplines": discipline_count,
            "topics": topic_count,
            "lessons": lesson_count,
            "questions": question_count,
            "materials": material_count,
        }

    def cleanup_unused_data(self) -> dict:
        counts = self.get_unused_data_counts()
        with self.db.get_connection() as conn:
            conn.execute(
                """
                DELETE FROM educational_programs
                WHERE NOT EXISTS (
                    SELECT 1 FROM program_disciplines pd WHERE pd.program_id = educational_programs.id
                )
                AND NOT EXISTS (
                    SELECT 1 FROM program_topics pt WHERE pt.program_id = educational_programs.id
                )
                """
            )
            conn.execute(
                """
                DELETE FROM disciplines
                WHERE NOT EXISTS (
                    SELECT 1 FROM program_disciplines pd WHERE pd.discipline_id = disciplines.id
                )
                """
            )
            conn.execute(
                """
                DELETE FROM topics
                WHERE NOT EXISTS (
                    SELECT 1 FROM discipline_topics dt WHERE dt.topic_id = topics.id
                )
                AND NOT EXISTS (
                    SELECT 1 FROM program_topics pt WHERE pt.topic_id = topics.id
                )
                """
            )
            conn.execute(
                """
                DELETE FROM lessons
                WHERE NOT EXISTS (
                    SELECT 1 FROM topic_lessons tl WHERE tl.lesson_id = lessons.id
                )
                """
            )
            conn.execute(
                """
                DELETE FROM questions
                WHERE NOT EXISTS (
                    SELECT 1 FROM lesson_questions lq WHERE lq.question_id = questions.id
                )
                """
            )
            orphan_materials = conn.execute(
                """
                SELECT m.id FROM methodical_materials m
                WHERE NOT EXISTS (
                    SELECT 1 FROM material_associations ma WHERE ma.material_id = m.id
                )
                """
            ).fetchall()
        for row in orphan_materials:
            self.delete_material(row[0])
        return counts

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
