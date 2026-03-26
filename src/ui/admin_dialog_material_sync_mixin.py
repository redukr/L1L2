"""Material synchronization helpers extracted from AdminDialog."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from ..models.entities import MaterialType, MethodicalMaterial, Teacher
from ..services.teacher_sorting import teacher_sort_key


class AdminDialogMaterialSyncMixin:
    """Material sync behavior for AdminDialog."""

    def _material_author_labels(self, controller, material: MethodicalMaterial) -> tuple[str, ...]:  # noqa: ANN001
        teachers = list(material.teachers or [])
        if not teachers and hasattr(controller, "material_repo"):
            try:
                teachers = controller.material_repo.get_material_teachers(material.id)
            except (ValueError, RuntimeError, TypeError, sqlite3.Error) as exc:
                self._log_action("sync_material_author_lookup_failed", str(exc))
                teachers = []
        teachers = [t for t in teachers if t and t.full_name]
        teachers.sort(key=teacher_sort_key)
        return tuple(t.full_name for t in teachers)

    def _material_author_names(self, controller, material: MethodicalMaterial) -> set[str]:  # noqa: ANN001
        return set(self._material_author_labels(controller, material))

    def _safe_sync_material_path(self, path_value: str) -> Path | None:
        raw = (path_value or "").strip()
        if not raw:
            return None
        normalized = Path(raw.replace("\\", "/").lstrip("/"))
        root = Path(self.sync_source_files_root).resolve()
        candidate = (root / normalized).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            self._log_action("sync_material_path_rejected", raw)
            return None
        return candidate

    def _resolve_source_material_path(self, material: MethodicalMaterial) -> Path | None:
        if material.relative_path:
            return self._safe_sync_material_path(material.relative_path)
        if material.file_path:
            raw = material.file_path.strip()
            if Path(raw).is_absolute():
                self._log_action("sync_material_path_rejected", raw)
                return None
            return self._safe_sync_material_path(raw)
        return None

    def _unique_material_title(self, title: str, existing: set[str]) -> str:
        if title not in existing:
            return title
        index = 1
        while True:
            suffix = f"_{index:02d}"
            candidate = f"{title}{suffix}"
            if candidate not in existing:
                return candidate
            index += 1

    def _sync_materials_for_entity(
        self,
        source_entity_type: str,
        source_entity_id: int,
        target_entity_type: str,
        target_entity_id: int,
        target_program_id: int,
        target_discipline_id: int,
    ) -> None:
        if source_entity_type not in {"program", "discipline", "topic", "lesson"}:
            return
        materials = self.sync_source_admin.get_materials_for_entity(source_entity_type, source_entity_id)
        existing_titles = {m.title for m in self.controller.get_materials_for_entity(target_entity_type, target_entity_id)}
        material_types = {t.name for t in self.controller.get_material_types()}
        for material in materials:
            if material.material_type and material.material_type not in material_types:
                self.controller.add_material_type(MaterialType(name=material.material_type))
                material_types.add(material.material_type)
            title = self._unique_material_title(material.title, existing_titles)
            existing_titles.add(title)
            new_material = self.controller.add_material(
                MethodicalMaterial(
                    title=title,
                    material_type=material.material_type,
                    description=material.description,
                )
            )
            self.controller.add_material_to_entity(new_material.id, target_entity_type, target_entity_id)
            self._sync_material_authors(material, new_material)
            source_path = self._resolve_source_material_path(material)
            if source_path and source_path.exists():
                try:
                    self.controller.attach_material_file_with_context(
                        new_material, str(source_path), target_program_id, target_discipline_id
                    )
                except (ValueError, RuntimeError, OSError, TypeError, sqlite3.Error) as exc:
                    self._log_action("sync_material_attach_failed", str(exc))

    def _sync_material_authors(self, source_material: MethodicalMaterial, target_material: MethodicalMaterial) -> None:
        source_teachers = source_material.teachers
        if not source_teachers:
            try:
                source_teachers = self.sync_source_admin.material_repo.get_material_teachers(source_material.id)
            except (ValueError, RuntimeError, TypeError, sqlite3.Error) as exc:
                self._log_action("sync_material_teachers_read_failed", str(exc))
                source_teachers = []
        if not source_teachers:
            return
        if not hasattr(self, "_sync_teacher_cache"):
            self._sync_teacher_cache = {t.full_name: t for t in self.controller.get_teachers() if t.full_name}
        for teacher in source_teachers:
            if not teacher.full_name:
                continue
            target_teacher = self._sync_teacher_cache.get(teacher.full_name)
            if target_teacher is None:
                target_teacher = self.controller.add_teacher(
                    Teacher(
                        full_name=teacher.full_name,
                        military_rank=teacher.military_rank,
                        position=teacher.position,
                        department=teacher.department,
                        email=teacher.email,
                        phone=teacher.phone,
                    )
                )
                self._sync_teacher_cache[teacher.full_name] = target_teacher
            try:
                self.controller.add_teacher_to_material(target_teacher.id, target_material.id)
            except (ValueError, RuntimeError, TypeError, sqlite3.Error) as exc:
                self._log_action("sync_material_teacher_link_failed", str(exc))
