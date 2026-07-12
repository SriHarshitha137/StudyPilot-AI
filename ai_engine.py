"""Abstract contract for StudyPilot's pluggable AI engines."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIEngine(ABC):
    """Contract shared by rule-based and IBM Granite implementations."""

    @abstractmethod
    def generate_study_plan(self, profile: dict[str, Any]) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    def generate_revision_plan(self, profile: dict[str, Any]) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    def generate_daily_tasks(self, profile: dict[str, Any]) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    def generate_motivation(self, profile: dict[str, Any]) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def generate_subject_priority(self, profile: dict[str, Any]) -> list[dict[str, int | str]]:
        raise NotImplementedError

