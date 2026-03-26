"""Shared teacher sorting rules."""

from __future__ import annotations

from ..models.entities import Teacher


RANK_ORDER = [
    "генерал",
    "бригадний генерал",
    "полковник",
    "підполковник",
    "майор",
    "капітан",
    "старший лейтенант",
    "лейтенант",
    "молодший лейтенант",
]


def _surname_key(full_name: str | None) -> str:
    text = (full_name or "").strip()
    if not text:
        return ""
    parts = [part for part in text.split() if part]
    return (parts[0] if parts else text).casefold()


def _rank_index(rank: str | None) -> int:
    rank_lower = (rank or "").strip().casefold()
    if not rank_lower:
        return len(RANK_ORDER)
    ranked_tokens = sorted(enumerate(RANK_ORDER), key=lambda item: len(item[1]), reverse=True)
    for idx, token in ranked_tokens:
        if token in rank_lower:
            return idx
    return len(RANK_ORDER)


def teacher_sort_key(teacher: Teacher) -> tuple:
    order_index = teacher.order_index or 0
    if order_index > 0:
        return (0, order_index, (teacher.full_name or "").strip().casefold(), teacher.id or 0)

    position = (teacher.position or "").strip().casefold()
    department = (teacher.department or "").strip().casefold()
    rank = (teacher.military_rank or "").strip().casefold()
    surname = _surname_key(teacher.full_name)
    full_name = (teacher.full_name or "").strip().casefold()
    rank_idx = _rank_index(teacher.military_rank)

    is_zsu = ("працівник зсу" in rank) or ("зсу" in position) or ("зсу" in department)
    is_head = "начальник кафедри" in position
    is_deputy = "заступник начальника кафедри" in position
    is_docent = "доцент" in position
    is_senior = "старший викладач" in position
    is_teacher = ("викладач" in position) and not is_senior

    if is_zsu:
        group = 5
    elif is_head:
        group = 0
    elif is_deputy:
        group = 1
    elif is_docent:
        group = 2
    elif is_senior:
        group = 3
    elif is_teacher:
        group = 4
    else:
        group = 6

    if group in {3, 4}:
        return (1, group, rank_idx, surname, full_name, teacher.id or 0)
    return (1, group, surname, full_name, teacher.id or 0)
