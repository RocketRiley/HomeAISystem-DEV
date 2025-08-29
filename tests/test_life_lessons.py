from pathlib import Path
from scripts.life_lessons import LifeLessonManager


def test_add_and_revise_lesson(tmp_path):
    path = tmp_path / "lessons.json"
    mgr = LifeLessonManager(path)
    mgr.add_lesson("Be kind to others")
    lessons = mgr.list_lessons()
    assert len(lessons) == 1
    assert lessons[0]["topic"] == "Be kind to others"
    # Revise with negative evidence reduces stance
    mgr.revise_lesson("Be kind to others", evidence_strength=1.0, direction=-1.0)
    updated = mgr.list_lessons()[0]
    assert updated["stance"] < 1.0


def test_lesson_filtered(tmp_path):
    path = tmp_path / "lessons.json"
    mgr = LifeLessonManager(path, filter_level="pg13")
    mgr.add_lesson("Don't say fuck")
    lesson = mgr.list_lessons()[0]
    assert "frick" in lesson["topic"]
