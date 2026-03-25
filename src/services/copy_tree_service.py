"""Helpers for duplicate/copy tree operations."""
from __future__ import annotations

from ..models.entities import Discipline, EducationalProgram, Lesson, MethodicalMaterial, Question, Topic


class CopyTreeService:
    """Owns deep-copy and duplicate workflows for curriculum entities."""

    def __init__(self, controller):
        self.controller = controller

    def duplicate_program(self, program_id: int) -> EducationalProgram:
        program = self.controller.program_repo.get_by_id(program_id)
        if not program:
            raise ValueError("Program not found.")
        new_program = EducationalProgram(
            name=self.controller.copy_name(program.name),
            description=program.description,
            level=program.level,
            year=program.year,
            duration_hours=program.duration_hours,
        )
        new_program = self.controller.program_repo.add(new_program)
        for discipline in self.controller.program_repo.get_program_disciplines(program_id):
            order_index = self.controller.get_next_order_index("program_disciplines", "program_id", new_program.id)
            self.controller.program_repo.add_discipline_to_program(new_program.id, discipline.id, order_index)
        for material in self.controller.material_repo.get_materials_for_entity("program", program_id):
            self.controller.material_repo.add_material_to_entity(material.id, "program", new_program.id)
        return new_program

    def copy_program(self, program_id: int) -> EducationalProgram:
        program = self.controller.program_repo.get_by_id(program_id)
        if not program:
            raise ValueError("Program not found.")
        new_program = EducationalProgram(
            name=self.controller.copy_name(program.name),
            description=program.description,
            level=program.level,
            year=program.year,
            duration_hours=program.duration_hours,
        )
        new_program = self.controller.program_repo.add(new_program)
        material_map: dict[int, MethodicalMaterial] = {}
        discipline_map: dict[int, Discipline] = {}
        for discipline in self.controller.program_repo.get_program_disciplines(program_id):
            new_discipline = self.copy_discipline_tree(discipline, new_program.id, material_map, discipline.order_index)
            discipline_map[discipline.id] = new_discipline
        for material in self.controller.material_repo.get_materials_for_entity("program", program_id):
            discipline_id = next(iter(discipline_map.values())).id if discipline_map else None
            if discipline_id is None:
                continue
            new_material = self.copy_material(material, new_program.id, discipline_id, material_map)
            self.controller.material_repo.add_material_to_entity(new_material.id, "program", new_program.id)
        return new_program

    def duplicate_discipline(self, discipline_id: int, program_id: int) -> Discipline:
        discipline = self.controller.discipline_repo.get_by_id(discipline_id)
        if not discipline:
            raise ValueError("Discipline not found.")
        new_discipline = self.clone_discipline_links(discipline_id, rename=True)
        order_index = self.controller.get_next_order_index("program_disciplines", "program_id", program_id)
        self.controller.program_repo.add_discipline_to_program(program_id, new_discipline.id, order_index)
        return new_discipline

    def copy_discipline(self, discipline_id: int, program_id: int) -> Discipline:
        discipline = self.controller.discipline_repo.get_by_id(discipline_id)
        if not discipline:
            raise ValueError("Discipline not found.")
        return self.copy_discipline_tree(discipline, program_id, {})

    def duplicate_topic(self, topic_id: int, discipline_id: int) -> Topic:
        new_topic = self.clone_topic_links(topic_id, rename=True)
        order_index = self.controller.get_next_order_index("discipline_topics", "discipline_id", discipline_id)
        self.controller.discipline_repo.add_topic_to_discipline(discipline_id, new_topic.id, order_index)
        return new_topic

    def copy_topic(self, topic_id: int, discipline_id: int) -> Topic:
        topic = self.controller.topic_repo.get_by_id(topic_id)
        if not topic:
            raise ValueError("Topic not found.")
        program_id, _ = self.controller.resolve_program_discipline_for_entity("discipline", discipline_id)
        return self.copy_topic_tree(topic, program_id, discipline_id, {})

    def duplicate_lesson(self, lesson_id: int, topic_id: int) -> Lesson:
        new_lesson = self.clone_lesson_links(lesson_id, rename=True)
        order_index = self.controller.get_next_order_index("topic_lessons", "topic_id", topic_id)
        self.controller.topic_repo.add_lesson_to_topic(topic_id, new_lesson.id, order_index)
        return new_lesson

    def copy_lesson(self, lesson_id: int, topic_id: int) -> Lesson:
        lesson = self.controller.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise ValueError("Lesson not found.")
        program_id, discipline_id = self.controller.resolve_program_discipline_for_entity("topic", topic_id)
        return self.copy_lesson_tree(lesson, topic_id, program_id, discipline_id, {})

    def duplicate_question(self, question_id: int, lesson_id: int) -> Question:
        question = self.controller.question_repo.get_by_id(question_id)
        if not question:
            raise ValueError("Question not found.")
        new_question = Question(
            content=question.content,
            answer=question.answer,
            order_index=question.order_index,
        )
        new_question = self.controller.question_repo.add(new_question)
        order_index = self.controller.get_next_order_index("lesson_questions", "lesson_id", lesson_id)
        self.controller.lesson_repo.add_question_to_lesson(lesson_id, new_question.id, order_index)
        return new_question

    def copy_question(self, question_id: int, lesson_id: int) -> Question:
        return self.duplicate_question(question_id, lesson_id)

    def copy_discipline_tree(self, discipline: Discipline, program_id: int, material_map: dict[int, MethodicalMaterial], order_index: int | None = None) -> Discipline:
        new_discipline = Discipline(
            name=self.controller.copy_name(discipline.name),
            description=discipline.description,
            order_index=discipline.order_index,
        )
        new_discipline = self.controller.discipline_repo.add(new_discipline)
        order_index = order_index if order_index is not None else self.controller.get_next_order_index("program_disciplines", "program_id", program_id)
        self.controller.program_repo.add_discipline_to_program(program_id, new_discipline.id, order_index)
        for teacher in self.controller.teacher_repo.get_teachers_for_disciplines([discipline.id]):
            self.controller.teacher_repo.add_discipline(teacher.id, new_discipline.id)
        for topic in self.controller.discipline_repo.get_discipline_topics(discipline.id):
            self.copy_topic_tree(topic, program_id, new_discipline.id, material_map, topic.order_index)
        for material in self.controller.material_repo.get_materials_for_entity("discipline", discipline.id):
            new_material = self.copy_material(material, program_id, new_discipline.id, material_map)
            self.controller.material_repo.add_material_to_entity(new_material.id, "discipline", new_discipline.id)
        return new_discipline

    def copy_topic_tree(self, topic: Topic, program_id: int, discipline_id: int, material_map: dict[int, MethodicalMaterial], order_index: int | None = None) -> Topic:
        new_topic = Topic(
            title=self.controller.copy_name(topic.title),
            description=topic.description,
            order_index=topic.order_index,
        )
        new_topic = self.controller.topic_repo.add(new_topic)
        order_index = order_index if order_index is not None else self.controller.get_next_order_index("discipline_topics", "discipline_id", discipline_id)
        self.controller.discipline_repo.add_topic_to_discipline(discipline_id, new_topic.id, order_index)
        for lesson, order in self.controller.get_topic_lessons_with_order(topic.id):
            self.copy_lesson_tree(lesson, new_topic.id, program_id, discipline_id, material_map, order)
        for material in self.controller.material_repo.get_materials_for_entity("topic", topic.id):
            new_material = self.copy_material(material, program_id, discipline_id, material_map)
            self.controller.material_repo.add_material_to_entity(new_material.id, "topic", new_topic.id)
        return new_topic

    def copy_lesson_tree(self, lesson: Lesson, topic_id: int, program_id: int, discipline_id: int, material_map: dict[int, MethodicalMaterial], order_index: int | None = None) -> Lesson:
        new_lesson = Lesson(
            title=self.controller.copy_name(lesson.title),
            description=lesson.description,
            duration_hours=lesson.duration_hours,
            lesson_type_id=lesson.lesson_type_id,
            classroom_hours=lesson.classroom_hours,
            self_study_hours=lesson.self_study_hours,
            order_index=lesson.order_index,
        )
        new_lesson = self.controller.lesson_repo.add(new_lesson)
        order_index = order_index if order_index is not None else self.controller.get_next_order_index("topic_lessons", "topic_id", topic_id)
        self.controller.topic_repo.add_lesson_to_topic(topic_id, new_lesson.id, order_index)
        for question, q_order in self.controller.get_lesson_questions_with_order(lesson.id):
            new_question = Question(content=question.content, answer=question.answer, order_index=question.order_index)
            new_question = self.controller.question_repo.add(new_question)
            self.controller.lesson_repo.add_question_to_lesson(new_lesson.id, new_question.id, q_order)
        for material in self.controller.material_repo.get_materials_for_entity("lesson", lesson.id):
            new_material = self.copy_material(material, program_id, discipline_id, material_map)
            self.controller.material_repo.add_material_to_entity(new_material.id, "lesson", new_lesson.id)
        return new_lesson

    def copy_material(self, material: MethodicalMaterial, program_id: int, discipline_id: int, material_map: dict[int, MethodicalMaterial]) -> MethodicalMaterial:
        if material.id in material_map:
            return material_map[material.id]
        new_material = MethodicalMaterial(title=material.title, material_type=material.material_type, description=material.description)
        new_material = self.controller.material_repo.add(new_material)
        for teacher in self.controller.material_repo.get_material_teachers(material.id):
            self.controller.material_repo.add_teacher_to_material(teacher.id, new_material.id)
        if material.relative_path and program_id and discipline_id:
            source_path = str(self.controller.resolve_material_storage_path(material.relative_path))
            self.controller.attach_material_file_with_context(new_material, source_path, program_id, discipline_id)
        material_map[material.id] = new_material
        return new_material

    def clone_discipline_links(self, discipline_id: int, rename: bool = True) -> Discipline:
        discipline = self.controller.discipline_repo.get_by_id(discipline_id)
        name = self.controller.copy_name(discipline.name) if rename else discipline.name
        new_discipline = Discipline(name=name, description=discipline.description, order_index=discipline.order_index)
        new_discipline = self.controller.discipline_repo.add(new_discipline)
        for discipline_topic in self.controller.discipline_repo.get_discipline_topics(discipline_id):
            self.controller.discipline_repo.add_topic_to_discipline(new_discipline.id, discipline_topic.id, discipline_topic.order_index)
        for material in self.controller.material_repo.get_materials_for_entity("discipline", discipline_id):
            self.controller.material_repo.add_material_to_entity(material.id, "discipline", new_discipline.id)
        for teacher in self.controller.teacher_repo.get_teachers_for_disciplines([discipline_id]):
            self.controller.teacher_repo.add_discipline(teacher.id, new_discipline.id)
        return new_discipline

    def clone_topic_links(self, topic_id: int, rename: bool = True) -> Topic:
        topic = self.controller.topic_repo.get_by_id(topic_id)
        title = self.controller.copy_name(topic.title) if rename else topic.title
        new_topic = Topic(title=title, description=topic.description, order_index=topic.order_index)
        new_topic = self.controller.topic_repo.add(new_topic)
        for lesson, order in self.controller.get_topic_lessons_with_order(topic_id):
            self.controller.topic_repo.add_lesson_to_topic(new_topic.id, lesson.id, order)
        for material in self.controller.material_repo.get_materials_for_entity("topic", topic_id):
            self.controller.material_repo.add_material_to_entity(material.id, "topic", new_topic.id)
        return new_topic

    def clone_lesson_links(self, lesson_id: int, rename: bool = True) -> Lesson:
        lesson = self.controller.lesson_repo.get_by_id(lesson_id)
        title = self.controller.copy_name(lesson.title) if rename else lesson.title
        new_lesson = Lesson(
            title=title,
            description=lesson.description,
            duration_hours=lesson.duration_hours,
            lesson_type_id=lesson.lesson_type_id,
            classroom_hours=lesson.classroom_hours,
            self_study_hours=lesson.self_study_hours,
            order_index=lesson.order_index,
        )
        new_lesson = self.controller.lesson_repo.add(new_lesson)
        for question, q_order in self.controller.get_lesson_questions_with_order(lesson_id):
            self.controller.lesson_repo.add_question_to_lesson(new_lesson.id, question.id, q_order)
        for material in self.controller.material_repo.get_materials_for_entity("lesson", lesson_id):
            self.controller.material_repo.add_material_to_entity(material.id, "lesson", new_lesson.id)
        return new_lesson
