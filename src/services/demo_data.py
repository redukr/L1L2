"""Demo data bootstrap for first-time use."""
from datetime import datetime
from ..models.database import Database
from ..models.entities import (
    Teacher,
    EducationalProgram,
    Discipline,
    Topic,
    Lesson,
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


def seed_demo_data(database: Database) -> None:
    """Insert demo data if the database is empty."""
    with database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM educational_programs")
        if cursor.fetchone()["count"] > 0:
            return

    teacher_repo = TeacherRepository(database)
    program_repo = ProgramRepository(database)
    discipline_repo = DisciplineRepository(database)
    topic_repo = TopicRepository(database)
    lesson_repo = LessonRepository(database)
    lesson_type_repo = LessonTypeRepository(database)
    question_repo = QuestionRepository(database)
    material_repo = MaterialRepository(database)

    teachers = [
        Teacher(
            full_name="Dana Whitaker",
            position="Instructional Designer",
            department="Learning Development",
            email="dana.whitaker@academy.local",
            phone="+1-202-555-0184",
        ),
        Teacher(
            full_name="Luis Mendoza",
            position="Senior Lecturer",
            department="Data Science",
            email="luis.mendoza@academy.local",
            phone="+1-202-555-0147",
        ),
        Teacher(
            full_name="Nora Patel",
            position="Associate Professor",
            department="Applied Mathematics",
            email="nora.patel@academy.local",
            phone="+1-202-555-0199",
        ),
    ]

    teachers = [teacher_repo.add(t) for t in teachers]

    current_year = datetime.now().year
    program = program_repo.add(EducationalProgram(
        name="Foundations of Data Literacy",
        description="A practical program covering data collection, interpretation, and communication.",
        level="Undergraduate",
        year=current_year,
        duration_hours=48,
    ))

    program2 = program_repo.add(EducationalProgram(
        name="Applied Statistics for Decision Making",
        description="Statistical methods and tools for evidence-based decisions.",
        level="Professional Certificate",
        year=current_year,
        duration_hours=60,
    ))

    disciplines = [
        Discipline(
            name="Data Foundations",
            description="Core foundations for working with data responsibly.",
            order_index=1,
        ),
        Discipline(
            name="Communication and Visualization",
            description="Presenting insights clearly and effectively.",
            order_index=2,
        ),
        Discipline(
            name="Statistical Reasoning",
            description="Inference and probability for decision making.",
            order_index=1,
        ),
    ]
    disciplines = [discipline_repo.add(d) for d in disciplines]

    topics = [
        Topic(
            title="Data Collection and Ethics",
            description="Sources of data, consent, and responsible handling.",
            order_index=1,
        ),
        Topic(
            title="Data Types and Structures",
            description="Qualitative and quantitative data with common structures.",
            order_index=2,
        ),
        Topic(
            title="Visual Communication",
            description="Effective charts and storytelling with data.",
            order_index=3,
        ),
        Topic(
            title="Probability Foundations",
            description="Probability rules, conditional probability, and distributions.",
            order_index=1,
        ),
        Topic(
            title="Inferential Methods",
            description="Confidence intervals and hypothesis testing in practice.",
            order_index=2,
        ),
    ]
    topics = [topic_repo.add(t) for t in topics]

    program_repo.add_discipline_to_program(program.id, disciplines[0].id, 1)
    program_repo.add_discipline_to_program(program.id, disciplines[1].id, 2)
    program_repo.add_discipline_to_program(program2.id, disciplines[2].id, 1)

    discipline_repo.add_topic_to_discipline(disciplines[0].id, topics[0].id, 1)
    discipline_repo.add_topic_to_discipline(disciplines[0].id, topics[1].id, 2)
    discipline_repo.add_topic_to_discipline(disciplines[1].id, topics[2].id, 1)
    discipline_repo.add_topic_to_discipline(disciplines[2].id, topics[3].id, 1)
    discipline_repo.add_topic_to_discipline(disciplines[2].id, topics[4].id, 2)

    lesson_types = {lt.name: lt.id for lt in lesson_type_repo.get_all()}
    lessons = [
        Lesson(
            title="Ethical Data Sourcing",
            description="Planning data collection with consent and transparency.",
            duration_hours=2.0,
            lesson_type_id=lesson_types.get("Лекція"),
            order_index=1,
        ),
        Lesson(
            title="Survey Design Workshop",
            description="Drafting survey questions and avoiding bias.",
            duration_hours=2.5,
            lesson_type_id=lesson_types.get("Практичне заняття"),
            order_index=2,
        ),
        Lesson(
            title="Data Types Overview",
            description="Identifying data types and choosing formats.",
            duration_hours=2.0,
            lesson_type_id=lesson_types.get("Лекція"),
            order_index=1,
        ),
        Lesson(
            title="Tabular Data Structures",
            description="Designing clean tables and data dictionaries.",
            duration_hours=2.0,
            lesson_type_id=lesson_types.get("Практичне заняття"),
            order_index=2,
        ),
        Lesson(
            title="Chart Selection",
            description="Choosing the right chart for the message.",
            duration_hours=1.5,
            lesson_type_id=lesson_types.get("Семінар"),
            order_index=1,
        ),
        Lesson(
            title="Distributions and Expectations",
            description="Key distributions and expected values.",
            duration_hours=2.0,
            lesson_type_id=lesson_types.get("Лекція"),
            order_index=1,
        ),
        Lesson(
            title="Hypothesis Testing",
            description="Designing and interpreting tests.",
            duration_hours=2.5,
            lesson_type_id=lesson_types.get("Групове заняття"),
            order_index=2,
        ),
    ]
    lessons = [lesson_repo.add(l) for l in lessons]

    topic_repo.add_lesson_to_topic(topics[0].id, lessons[0].id, 1)
    topic_repo.add_lesson_to_topic(topics[0].id, lessons[1].id, 2)
    topic_repo.add_lesson_to_topic(topics[1].id, lessons[2].id, 1)
    topic_repo.add_lesson_to_topic(topics[1].id, lessons[3].id, 2)
    topic_repo.add_lesson_to_topic(topics[2].id, lessons[4].id, 1)
    topic_repo.add_lesson_to_topic(topics[3].id, lessons[5].id, 1)
    topic_repo.add_lesson_to_topic(topics[4].id, lessons[6].id, 1)

    questions = [
        Question(
            content="Why is informed consent required when collecting personal data?",
            answer="It ensures participants understand how their data will be used and can agree knowingly.",
            difficulty_level=1,
            order_index=1,
        ),
        Question(
            content="Name two common sources of selection bias in surveys.",
            answer="Voluntary response bias and undercoverage of key groups.",
            difficulty_level=2,
            order_index=2,
        ),
        Question(
            content="Give an example of categorical data and numeric data.",
            answer="Categorical: customer segment; numeric: monthly revenue.",
            difficulty_level=1,
            order_index=1,
        ),
        Question(
            content="When is a bar chart more appropriate than a line chart?",
            answer="When comparing discrete categories rather than trends over time.",
            difficulty_level=1,
            order_index=1,
        ),
        Question(
            content="What does a 95% confidence interval represent?",
            answer="A range that would contain the true parameter 95% of the time in repeated samples.",
            difficulty_level=3,
            order_index=1,
        ),
    ]
    questions = [question_repo.add(q) for q in questions]

    lesson_repo.add_question_to_lesson(lessons[0].id, questions[0].id, 1)
    lesson_repo.add_question_to_lesson(lessons[1].id, questions[1].id, 1)
    lesson_repo.add_question_to_lesson(lessons[2].id, questions[2].id, 1)
    lesson_repo.add_question_to_lesson(lessons[4].id, questions[3].id, 1)
    lesson_repo.add_question_to_lesson(lessons[6].id, questions[4].id, 1)

    materials = [
        MethodicalMaterial(
            title="Lesson Plan: Data Collection Workshop",
            material_type="plan",
            description="Step-by-step plan for the survey design workshop.",
        ),
        MethodicalMaterial(
            title="Methodical Guide: Survey Design",
            material_type="guide",
            description="Guidelines for constructing balanced survey questions.",
        ),
        MethodicalMaterial(
            title="Slides: Descriptive Statistics",
            material_type="presentation",
            description="Slide deck covering descriptive statistics concepts.",
        ),
        MethodicalMaterial(
            title="Attachment: Data Dictionary Template",
            material_type="attachment",
            description="Template for documenting datasets and variables.",
        ),
    ]
    materials = [material_repo.add(m) for m in materials]

    material_repo.add_teacher_to_material(teachers[0].id, materials[0].id)
    material_repo.add_teacher_to_material(teachers[0].id, materials[1].id)
    material_repo.add_teacher_to_material(teachers[1].id, materials[2].id)
    material_repo.add_teacher_to_material(teachers[2].id, materials[3].id)

    material_repo.add_material_to_entity(materials[0].id, "lesson", lessons[1].id)
    material_repo.add_material_to_entity(materials[1].id, "topic", topics[0].id)
    material_repo.add_material_to_entity(materials[2].id, "program", program2.id)
    material_repo.add_material_to_entity(materials[3].id, "lesson", lessons[3].id)
