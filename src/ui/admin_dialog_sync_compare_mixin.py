"""Sync compare helpers extracted from AdminDialog."""

from __future__ import annotations

import zlib
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QTreeWidgetItem

from ..models.entities import EducationalProgram, MethodicalMaterial


class AdminDialogSyncCompareMixin:
    """Methods for comparing and annotating sync trees."""

    def _set_check_state_recursive(self, item: QTreeWidgetItem, state: Qt.CheckState) -> None:
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self._set_check_state_recursive(child, state)

    def _is_identical_entity(
        self,
        entity_type: str,
        source_entity,
        target_entity,
        source_controller,
        source_files_root: Path,
        target_controller,
        target_files_root: Path,
    ) -> bool:  # noqa: ANN001
        source_sig = self._entity_signature(
            source_controller, entity_type, source_entity, source_files_root, {}
        )
        target_sig = self._entity_signature(
            target_controller, entity_type, target_entity, target_files_root, {}
        )
        return source_sig == target_sig

    def _entity_signature(
        self,
        controller,
        entity_type: str,
        entity,
        files_root: Path,
        cache: dict,
    ) -> tuple:  # noqa: ANN001
        cache_key = (entity_type, getattr(entity, "id", None), str(files_root))
        if cache_key in cache:
            return cache[cache_key]
        if entity_type == "lesson":
            questions = controller.lesson_repo.get_lesson_questions(entity.id)
            q_sig = tuple(sorted(q.content for q in questions))
            m_sig = tuple(self._materials_signature(controller, "lesson", entity.id, files_root))
            sig = ("lesson", q_sig, m_sig)
        elif entity_type == "topic":
            lessons = controller.topic_repo.get_topic_lessons(entity.id)
            l_sig = tuple(
                sorted(
                    (
                        lesson.title,
                        self._entity_signature(controller, "lesson", lesson, files_root, cache),
                    )
                    for lesson in lessons
                )
            )
            m_sig = tuple(self._materials_signature(controller, "topic", entity.id, files_root))
            sig = ("topic", l_sig, m_sig)
        elif entity_type == "discipline":
            topics = controller.discipline_repo.get_discipline_topics(entity.id)
            t_sig = tuple(
                sorted(
                    (
                        topic.title,
                        self._entity_signature(controller, "topic", topic, files_root, cache),
                    )
                    for topic in topics
                )
            )
            m_sig = tuple(self._materials_signature(controller, "discipline", entity.id, files_root))
            sig = ("discipline", t_sig, m_sig)
        elif entity_type == "program":
            disciplines = controller.program_repo.get_program_disciplines(entity.id)
            d_sig = tuple(
                sorted(
                    (
                        disc.name,
                        self._entity_signature(controller, "discipline", disc, files_root, cache),
                    )
                    for disc in disciplines
                )
            )
            m_sig = tuple(self._materials_signature(controller, "program", entity.id, files_root))
            sig = ("program", d_sig, m_sig)
        else:
            sig = (entity_type, getattr(entity, "id", None))
        cache[cache_key] = sig
        return sig

    def _materials_signature(
        self,
        controller,
        entity_type: str,
        entity_id: int,
        files_root: Path,
    ) -> list[tuple]:  # noqa: ANN001
        materials = controller.get_materials_for_entity(entity_type, entity_id)
        sig = []
        for material in materials:
            crc = self._material_crc(material, files_root)
            authors = self._material_author_labels(controller, material)
            sig.append((material.title, material.material_type, crc, authors))
        return sorted(sig)

    def _material_crc(self, material: MethodicalMaterial, files_root: Path) -> int:
        path = None
        if material.relative_path:
            path = files_root / material.relative_path
        elif material.file_path:
            path = Path(material.file_path)
            if not path.is_absolute():
                path = files_root / material.file_path
        if not path or not path.exists():
            return 0
        checksum = 0
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                checksum = zlib.crc32(chunk, checksum)
        return checksum & 0xFFFFFFFF

    def _build_sync_compare_index_for_program(self, controller, program: EducationalProgram) -> dict:  # noqa: ANN001
        programs = {program.name: program}
        disciplines = {program.id: {d.name: d for d in controller.get_program_disciplines(program.id)}}
        topics = {}
        lessons = {}
        for discipline in disciplines[program.id].values():
            topics[discipline.id] = {
                t.title: t for t in controller.discipline_repo.get_discipline_topics(discipline.id)
            }
            for topic in topics[discipline.id].values():
                lessons[topic.id] = {l.title: l for l in controller.topic_repo.get_topic_lessons(topic.id)}
        return {
            "programs": programs,
            "selected_program": program,
            "disciplines": disciplines,
            "topics": topics,
            "lessons": lessons,
        }

    def _build_sync_compare_index(self, controller) -> dict:  # noqa: ANN001
        programs = {p.name: p for p in controller.get_programs()}
        disciplines = {}
        topics = {}
        lessons = {}
        for program in programs.values():
            disciplines[program.id] = {d.name: d for d in controller.get_program_disciplines(program.id)}
            for discipline in disciplines[program.id].values():
                topics[discipline.id] = {
                    t.title: t for t in controller.discipline_repo.get_discipline_topics(discipline.id)
                }
                for topic in topics[discipline.id].values():
                    lessons[topic.id] = {l.title: l for l in controller.topic_repo.get_topic_lessons(topic.id)}
        return {
            "programs": programs,
            "disciplines": disciplines,
            "topics": topics,
            "lessons": lessons,
        }

    def _materials_diff(self, entity_type: str, source_id: int, target_id: int | None) -> list[str]:
        if entity_type not in {"program", "discipline", "topic", "lesson"}:
            return []
        source_materials = self.sync_source_admin.get_materials_for_entity(entity_type, source_id)
        if not source_materials:
            return []
        if target_id is None:
            return [m.title for m in source_materials if m.title]
        target_materials = self.controller.get_materials_for_entity(entity_type, target_id)
        target_map = {
            (m.title, m.material_type): self._material_author_names(self.controller, m)
            for m in target_materials
        }
        missing = []
        for material in source_materials:
            key = (material.title, material.material_type)
            source_authors = self._material_author_names(self.sync_source_admin, material)
            if key not in target_map:
                missing.append(material.title)
            elif source_authors != target_map.get(key, set()):
                missing.append(material.title)
        return missing

    def _mark_materials_diff(self, item: QTreeWidgetItem, _missing: list[str]) -> None:
        item.setBackground(0, QBrush(QColor(255, 242, 204)))
        item.setForeground(0, QBrush(QColor(0, 0, 0)))

    def _append_material_children(
        self,
        controller,
        entity_type: str,
        entity_id: int,
        parent_item: QTreeWidgetItem,
        target_controller=None,
        target_entity_id: int | None = None,
    ) -> None:  # noqa: ANN001
        if not hasattr(controller, "get_materials_for_entity"):
            return
        materials = controller.get_materials_for_entity(entity_type, entity_id)
        if not materials:
            return
        target_map = {}
        if target_controller and target_entity_id is not None:
            target_materials = target_controller.get_materials_for_entity(entity_type, target_entity_id)
            target_map = {
                (m.title, m.material_type): self._material_author_names(target_controller, m)
                for m in target_materials
            }
        header = QTreeWidgetItem([self.tr("Materials")])
        header.setForeground(0, QBrush(QColor(0, 128, 0)))
        header.setBackground(0, QBrush(QColor(226, 239, 218)))
        header.setFlags(header.flags() & ~Qt.ItemIsUserCheckable)
        for material in materials:
            title = material.title or ""
            label = f"• {title}"
            author_names = self._material_author_labels(controller, material)
            teachers = ", ".join(author_names) if author_names else ""
            if teachers:
                label += f" | {self.tr('Teachers')}: {teachers}"
            item = QTreeWidgetItem([label])
            item.setForeground(0, QBrush(QColor(0, 128, 0)))
            item.setBackground(0, QBrush(QColor(240, 248, 235)))
            item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
            if target_map:
                key = (material.title, material.material_type)
                source_authors = self._material_author_names(controller, material)
                if key in target_map and source_authors != target_map.get(key, set()):
                    item.setBackground(0, QBrush(QColor(255, 242, 204)))
                    item.setForeground(0, QBrush(QColor(0, 0, 0)))
            header.addChild(item)
        parent_item.addChild(header)
