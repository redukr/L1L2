"""Main controller for user-mode interactions."""
from typing import Dict, List, Optional, Tuple
from ..models.database import Database
from ..models.entities import EducationalProgram, Discipline, Topic, Lesson, Question, MethodicalMaterial, SearchResult
from ..repositories.program_repository import ProgramRepository
from ..repositories.discipline_repository import DisciplineRepository
from ..repositories.topic_repository import TopicRepository
from ..repositories.lesson_repository import LessonRepository
from ..repositories.question_repository import QuestionRepository
from ..repositories.material_repository import MaterialRepository
from ..repositories.teacher_repository import TeacherRepository
from ..services.search_service import SearchService


class MainController:
    """Coordinates user-mode UI with repositories and services."""

    def __init__(self, database: Database):
        self.db = database
        self.program_repo = ProgramRepository(database)
        self.discipline_repo = DisciplineRepository(database)
        self.topic_repo = TopicRepository(database)
        self.lesson_repo = LessonRepository(database)
        self.question_repo = QuestionRepository(database)
        self.material_repo = MaterialRepository(database)
        self.teacher_repo = TeacherRepository(database)
        self.search_service = SearchService(database)

    def get_programs(self) -> List[EducationalProgram]:
        return self.program_repo.get_all()

    def get_program_structure(self, program_id: int) -> List[Discipline]:
        disciplines = self.program_repo.get_program_disciplines(program_id)
        for discipline in disciplines:
            discipline.topics = self.discipline_repo.get_discipline_topics(discipline.id)
            for topic in discipline.topics:
                topic.lessons = self.topic_repo.get_topic_lessons(topic.id)
                for lesson in topic.lessons:
                    lesson.questions = self.lesson_repo.get_lesson_questions(lesson.id)
        return disciplines

    def get_program_disciplines(self, program_id: int) -> List[Discipline]:
        return self.program_repo.get_program_disciplines(program_id)

    def get_entity_details(self, entity_type: str, entity_id: int) -> Dict[str, object]:
        if entity_type == "program":
            program = self.program_repo.get_by_id(entity_id)
            if not program:
                return {}
            return {
                "title": program.name,
                "description": program.description or "",
                "meta": {
                    "level": program.level or "",
                    "year": program.year or "",
                    "duration_hours": program.duration_hours or 0,
                },
            }
        if entity_type == "discipline":
            discipline = self.discipline_repo.get_by_id(entity_id)
            if not discipline:
                return {}
            return {
                "title": discipline.name,
                "description": discipline.description or "",
                "meta": {
                    "order_index": discipline.order_index,
                },
            }
        if entity_type == "topic":
            topic = self.topic_repo.get_by_id(entity_id)
            if not topic:
                return {}
            return {
                "title": topic.title,
                "description": topic.description or "",
                "meta": {
                    "order_index": topic.order_index,
                },
            }
        if entity_type == "lesson":
            lesson = self.lesson_repo.get_by_id(entity_id)
            if not lesson:
                return {}
            return {
                "title": lesson.title,
                "description": lesson.description or "",
                "meta": {
                    "duration_hours": lesson.duration_hours,
                    "order_index": lesson.order_index,
                    "lesson_type": lesson.lesson_type_name or "",
                    "classroom_hours": lesson.classroom_hours,
                    "self_study_hours": lesson.self_study_hours,
                },
            }
        if entity_type == "question":
            question = self.question_repo.get_by_id(entity_id)
            if not question:
                return {}
            return {
                "title": question.content,
                "description": "",
                "meta": {},
            }
        if entity_type == "material":
            material = self.material_repo.get_by_id(entity_id)
            if not material:
                return {}
            teachers = ", ".join(t.full_name for t in material.teachers) or ""
            file_name = material.original_filename or material.file_name or ""
            return {
                "title": material.title,
                "description": material.description or "",
                "meta": {
                    "material_type": material.material_type,
                    "file_name": file_name,
                    "teachers": teachers,
                },
            }
        if entity_type == "teacher":
            teacher = self.teacher_repo.get_by_id(entity_id)
            if not teacher:
                return {}
            return {
                "title": teacher.full_name,
                "description": f"{teacher.position or ''} {teacher.department or ''}".strip(),
                "meta": {
                    "rank": teacher.military_rank or "",
                    "email": teacher.email or "",
                    "phone": teacher.phone or "",
                },
            }
        return {}

    def get_materials_for_entity(self, entity_type: str, entity_id: int) -> List[MethodicalMaterial]:
        if entity_type not in {"program", "discipline", "topic", "lesson"}:
            return []
        return self.material_repo.get_materials_for_entity(entity_type, entity_id)

    def get_teachers_for_disciplines(self, discipline_ids: List[int]):
        return self.teacher_repo.get_teachers_for_disciplines(discipline_ids)

    def search(self, keyword: str) -> List[SearchResult]:
        return self.search_service.search_all(keyword)

    def resolve_search_navigation(self, result: SearchResult) -> Dict[str, Optional[int]]:
        target = {
            "program_id": None,
            "discipline_id": None,
            "topic_id": None,
            "lesson_id": None,
            "question_id": None,
        }
        if result.entity_type == "program":
            target["program_id"] = result.entity_id
            return target
        if result.entity_type == "discipline":
            programs = self.program_repo.get_programs_for_discipline(result.entity_id)
            target["program_id"] = programs[0].id if programs else None
            target["discipline_id"] = result.entity_id
            return target
        if result.entity_type == "topic":
            programs = self.program_repo.get_programs_for_topic(result.entity_id)
            target["program_id"] = programs[0].id if programs else None
            disciplines = self.discipline_repo.get_disciplines_for_topic(result.entity_id)
            target["discipline_id"] = disciplines[0].id if disciplines else None
            target["topic_id"] = result.entity_id
            return target
        if result.entity_type == "lesson":
            programs = self.program_repo.get_programs_for_lesson(result.entity_id)
            target["program_id"] = programs[0].id if programs else None
            disciplines = self.discipline_repo.get_disciplines_for_lesson(result.entity_id)
            target["discipline_id"] = disciplines[0].id if disciplines else None
            topics = self.topic_repo.get_topics_for_lesson(result.entity_id)
            target["topic_id"] = topics[0].id if topics else None
            target["lesson_id"] = result.entity_id
            return target
        if result.entity_type == "question":
            programs = self.program_repo.get_programs_for_question(result.entity_id)
            target["program_id"] = programs[0].id if programs else None
            lessons = self.lesson_repo.get_lessons_for_question(result.entity_id)
            target["lesson_id"] = lessons[0].id if lessons else None
            disciplines = self.discipline_repo.get_disciplines_for_question(result.entity_id)
            target["discipline_id"] = disciplines[0].id if disciplines else None
            topics = self.topic_repo.get_topics_for_question(result.entity_id)
            target["topic_id"] = topics[0].id if topics else None
            target["question_id"] = result.entity_id
            return target
        if result.entity_type == "material":
            associations = self.material_repo.get_material_associations(result.entity_id)
            if associations:
                entity_type, entity_id = associations[0]
                if entity_type == "program":
                    target["program_id"] = entity_id
                if entity_type == "discipline":
                    programs = self.program_repo.get_programs_for_discipline(entity_id)
                    target["program_id"] = programs[0].id if programs else None
                    target["discipline_id"] = entity_id
                if entity_type == "topic":
                    programs = self.program_repo.get_programs_for_topic(entity_id)
                    target["program_id"] = programs[0].id if programs else None
                    disciplines = self.discipline_repo.get_disciplines_for_topic(entity_id)
                    target["discipline_id"] = disciplines[0].id if disciplines else None
                    target["topic_id"] = entity_id
                if entity_type == "lesson":
                    programs = self.program_repo.get_programs_for_lesson(entity_id)
                    target["program_id"] = programs[0].id if programs else None
                    disciplines = self.discipline_repo.get_disciplines_for_lesson(entity_id)
                    target["discipline_id"] = disciplines[0].id if disciplines else None
                    topics = self.topic_repo.get_topics_for_lesson(entity_id)
                    target["topic_id"] = topics[0].id if topics else None
                    target["lesson_id"] = entity_id
            return target
        return target
