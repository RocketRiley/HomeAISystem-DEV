# Life Lessons System

Clair distils high‑level principles from experience and stores them as
"life lessons".  Each lesson is represented internally as a strong
opinion managed by the existing `OpinionManager`.

* Lessons are **additive**: they can shape behaviour but never bypass or
  weaken the core `FilterPipeline` or other safety layers.
* Each lesson is filtered before it is stored so unsafe phrasing never
  persists on disk.
* Lessons carry high confidence but remain revisable.  New evidence can
  strengthen or weaken a lesson via `LifeLessonManager.revise_lesson`.
* Because lessons are opinions, they can be explained and updated using
  the same evidence log as other beliefs.

See `scripts/life_lessons.py` for the implementation.
