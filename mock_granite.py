"""A deterministic, useful default AI engine requiring no external API."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ai_engine import AIEngine
from utils import days_until, parse_exam_date


class MockGraniteAgent(AIEngine):
    """Rule-based agentic coordinator emulating a Granite-backed workflow."""

    QUOTES = [
        "Small, focused sessions today become calm confidence tomorrow.",
        "Progress is built by returning to the work, one page at a time.",
        "Your future result is shaped by the next focused 25 minutes.",
    ]

    def _subjects(self, profile: dict[str, Any]) -> list[str]:
        return profile.get("subjects") or ["Core Subject"]

    def _weak(self, profile: dict[str, Any]) -> list[str]:
        return profile.get("weak_subjects") or []

    def generate_subject_priority(self, profile: dict[str, Any]) -> list[dict[str, int | str]]:
        subjects, weak = self._subjects(profile), self._weak(profile)
        total_days = days_until(profile["exam_date"])
        urgency = 20 if total_days <= 14 else 10 if total_days <= 30 else 0
        priorities = []
        for index, subject in enumerate(subjects):
            score = min(100, 55 + urgency + (25 if subject in weak else 0) - index * 3)
            level = "High" if score >= 75 else "Medium" if score >= 60 else "Steady"
            priorities.append({"subject": subject, "score": score, "level": level})
        return sorted(priorities, key=lambda row: int(row["score"]), reverse=True)

    def generate_study_plan(self, profile: dict[str, Any]) -> list[dict[str, str]]:
        subjects, weak = self._subjects(profile), self._weak(profile)
        hours = max(1, int(profile.get("daily_study_hours", 3)))
        start, available = date.today(), max(7, min(14, days_until(profile["exam_date"]) or 7))
        plan = []
        for offset in range(available):
            first = weak[offset % len(weak)] if weak else subjects[offset % len(subjects)]
            second = subjects[(offset + 1) % len(subjects)]
            focus = "Practice problems and error review" if first in weak else "Learn concepts and make active-recall notes"
            plan.append({
                "day": (start + timedelta(days=offset)).strftime("%a, %d %b"),
                "focus": first,
                "hours": f"{max(1, round(hours * 0.6, 1))} hrs",
                "task": f"{focus}; then {second} for {max(1, round(hours * 0.4, 1))} hr.",
            })
        return plan

    def generate_revision_plan(self, profile: dict[str, Any]) -> list[dict[str, str]]:
        weak = self._weak(profile) or self._subjects(profile)
        remaining = days_until(profile["exam_date"])
        phases = [
            ("Foundation", "Revisit notes, formulas, and core concepts."),
            ("Active recall", "Use flashcards and explain topics without notes."),
            ("Timed practice", "Solve past questions and log mistakes."),
            ("Final review", "Review error log, summary sheets, and sleep well."),
        ]
        plan = []
        for index, (phase, action) in enumerate(phases):
            subject = weak[index % len(weak)]
            timing = f"Days {index * 3 + 1}-{min(remaining, index * 3 + 3)}" if remaining else "Start today"
            plan.append({"phase": phase, "when": timing, "subject": subject, "action": action})
        return plan

    def generate_daily_tasks(self, profile: dict[str, Any]) -> list[dict[str, str]]:
        hours = max(1, int(profile.get("daily_study_hours", 3)))
        priority = self.generate_subject_priority(profile)
        first = str(priority[0]["subject"])
        second = str(priority[1]["subject"]) if len(priority) > 1 else first
        pomodoros = max(2, hours * 2)
        return [
            {"task": f"Review {first} concepts", "duration": f"{pomodoros // 2} Pomodoros", "type": "Deep work"},
            {"task": f"Solve {first} practice questions", "duration": f"{pomodoros // 2} Pomodoros", "type": "Practice"},
            {"task": f"Create recall notes for {second}", "duration": "2 Pomodoros", "type": "Active recall"},
            {"task": "Update mistake log and plan tomorrow", "duration": "15 min", "type": "Reflection"},
        ]

    def generate_motivation(self, profile: dict[str, Any]) -> dict[str, str]:
        quote = self.QUOTES[days_until(profile["exam_date"]) % len(self.QUOTES)]
        tip = "Start with your highest-priority subject before checking messages."
        return {"quote": quote, "tip": tip}

