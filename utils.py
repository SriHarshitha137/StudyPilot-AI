"""Reusable utilities for validation, dates, and safe JSON persistence."""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).with_name("study_data.json")


def parse_subjects(value: str | list[str]) -> list[str]:
    """Normalize a comma-separated subject string or existing list."""
    items = value.split(",") if isinstance(value, str) else value
    return [str(item).strip() for item in items if str(item).strip()]


def parse_exam_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def days_until(exam_date: str) -> int:
    return max(0, (parse_exam_date(exam_date) - date.today()).days)


def load_student_data() -> dict[str, Any]:
    try:
        with DATA_FILE.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return default_student_data()


def save_student_data(data: dict[str, Any]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def default_student_data() -> dict[str, Any]:
    return {
        "student_name": "Student",
        "semester": "Semester 1",
        "exam_date": str(date.today()),
        "subjects": ["Mathematics", "Science"],
        "weak_subjects": ["Mathematics"],
        "daily_study_hours": 3,
        "target_percentage": 80,
        "completion_percentage": 0,
    }

