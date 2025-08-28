from __future__ import annotations

from pathlib import Path
from typing import Optional

from .llm_adapter import generate_response

class SkillAcquisitionManager:
    """Manage sandboxed, LLM-written skills with human approval."""

    def __init__(self, skills_dir: Optional[Path] = None) -> None:
        self.skills_dir = skills_dir or Path(__file__).resolve().parent / "generated_skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.pending_path = self.skills_dir / "pending_skill.py"

    def propose_skill(self, goal: str) -> Path:
        """Generate a new skill script for the given goal and store as pending."""
        prompt = (
            "You are a helpful assistant. Write a standalone Python script that fulfils the goal:\n"
            f"{goal}\nReturn only code."
        )
        code = generate_response(prompt, history=None, human_mode=False) or ""
        self.pending_path.write_text(code, encoding="utf-8")
        return self.pending_path

    def approve_skill(self, name: str) -> Path:
        """Approve the pending skill and activate it under the given name."""
        target = self.skills_dir / f"{name}.py"
        if self.pending_path.exists():
            self.pending_path.replace(target)
        return target

    def deny_skill(self) -> None:
        """Remove any pending skill without activating it."""
        if self.pending_path.exists():
            self.pending_path.unlink()
