#!/usr/bin/env python3
"""Simple task manager for Clair.

This module provides a basic to‑do list for Clair.  Tasks are
persisted in ``config/tasks.json``.  Each task has a unique ID,
description, due date (ISO format or date only), completion status
and optional tags.  The manager allows adding tasks, listing
tasks, marking tasks as complete and retrieving the next upcoming
task.

This is intended as a demonstration; in a real system you might
integrate with an external task service or calendar.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskManager:
    """Manage a simple to‑do list for Clair."""

    def __init__(self, path: Any) -> None:
        self.path = Path(path)
        self.tasks: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except Exception:
                self.tasks = []
        else:
            self.tasks = []

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2)
        except Exception:
            pass

    def add_task(self, description: str, due_date: str, tags: Optional[List[str]] = None) -> str:
        """Add a new task.

        Parameters
        ----------
        description: str
            A short description of the task.
        due_date: str
            Due date in ISO format (YYYY-MM-DD) or full datetime.
        tags: list of str, optional
            Tags or categories for the task.

        Returns
        -------
        str
            The ID of the newly created task.
        """
        task_id = str(uuid.uuid4())
        self.tasks.append({
            "id": task_id,
            "description": description,
            "due": due_date,
            "completed": False,
            "tags": tags or []
        })
        self._save()
        return task_id

    def list_tasks(self, completed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Return tasks filtered by completion status.

        Parameters
        ----------
        completed: bool or None
            If True, return only completed tasks.  If False, return
            only incomplete tasks.  If None, return all tasks.
        """
        if completed is None:
            return list(self.tasks)
        return [t for t in self.tasks if bool(t.get("completed")) == completed]

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed.

        Parameters
        ----------
        task_id: str
            The ID of the task to complete.

        Returns
        -------
        bool
            True if the task was found and marked complete, else False.
        """
        for task in self.tasks:
            if task.get("id") == task_id:
                task["completed"] = True
                self._save()
                return True
        return False

    def get_next_task(self, now: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Return the next incomplete task by due date.

        Parameters
        ----------
        now: datetime, optional
            The current time; unused here but could be used to filter
            overdue tasks differently.

        Returns
        -------
        dict or None
            The task with the earliest due date that is incomplete.
        """
        incomplete = [t for t in self.tasks if not t.get("completed")]
        if not incomplete:
            return None
        # Parse due as datetime if possible; tasks without due date are sorted last
        def parse_due(task: Dict[str, Any]) -> datetime:
            due = task.get("due")
            try:
                return datetime.fromisoformat(due) if due else datetime.max
            except Exception:
                return datetime.max
        incomplete.sort(key=parse_due)
        return incomplete[0]


__all__ = ["TaskManager"]