"""
Who may see what of a course.

Three levels:
    - ``full``    : instructor / admin. Everything, quiz answers included.
    - ``learner`` : enrolled student. Lesson content, but never the answers.
    - ``outline`` : anyone else. Titles, types and durations only.

Views serialize as usual, then pass the data through ``redact_*`` with the
caller's level.
"""
from __future__ import annotations

from rest_framework.exceptions import PermissionDenied

FULL = "full"
LEARNER = "learner"
OUTLINE = "outline"


def _is_admin(user) -> bool:
    role = getattr(user, "role", None)
    return bool(role and role.name in ("admin", "super_admin"))


def can_manage_course(user, course) -> bool:
    if not user or not user.is_authenticated:
        return False
    return bool(user.is_superuser or _is_admin(user) or course.instructor_id == user.id)


def is_enrolled(user, course_id: int) -> bool:
    if not user or not user.is_authenticated:
        return False
    from apps.enrollments.models import Enrollment

    return Enrollment.objects.filter(user_id=user.id, course_id=course_id).exists()


def content_level(user, course) -> str:
    if can_manage_course(user, course):
        return FULL
    if is_enrolled(user, course.id):
        return LEARNER
    return OUTLINE


def assert_can_view_content(user, course) -> str:
    """Return the caller's level, or raise if they may only see the outline."""
    level = content_level(user, course)
    if level == OUTLINE:
        raise PermissionDenied("Inscrivez-vous à ce cours pour accéder à son contenu.")
    return level


# --------------------------------------------------------------------------- #
# Redaction of serialized data
# --------------------------------------------------------------------------- #
def redact_question(data: dict, level: str) -> dict:
    if level == FULL:
        return data
    data = dict(data)
    data.pop("correct_answer_data", None)
    data["options"] = [
        {"text": opt.get("text")} for opt in (data.get("options") or []) if isinstance(opt, dict)
    ]
    return data


def redact_test(data: dict | None, level: str) -> dict | None:
    if not data or level == FULL:
        return data
    data = dict(data)
    questions = data.get("questions") or []
    if level == OUTLINE:
        data.pop("questions", None)
        data["question_count"] = len(questions)
    else:
        data["questions"] = [redact_question(q, level) for q in questions]
    return data


def redact_lesson(data: dict, level: str) -> dict:
    if level != OUTLINE:
        return data
    data = dict(data)
    data.pop("content_body", None)
    data.pop("video_url", None)
    return data


def redact_section(data: dict, level: str) -> dict:
    if level == FULL:
        return data
    data = dict(data)
    if level == OUTLINE:
        data.pop("text_content", None)
        data.pop("video_url", None)
    if "lessons" in data:
        data["lessons"] = [redact_lesson(l, level) for l in data["lessons"] or []]
    if "test" in data:
        data["test"] = redact_test(data["test"], level)
    return data


def redact_course(data: dict, level: str) -> dict:
    if level == FULL:
        return data
    data = dict(data)
    if "sections" in data:
        data["sections"] = [redact_section(s, level) for s in data["sections"] or []]
    return data
