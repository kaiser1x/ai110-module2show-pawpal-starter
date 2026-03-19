from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """Represents a single pet care task."""
    title: str
    duration_minutes: int
    priority: str
    preferred_time: str = "unspecified"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        pass


@dataclass
class Pet:
    """Represents a pet and its care tasks."""
    name: str
    species: str
    preferences: dict = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        pass


@dataclass
class Owner:
    """Represents a pet owner who manages multiple pets."""
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's list."""
        pass

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Find a pet by name."""
        pass


class Scheduler:
    """Builds and explains a daily schedule for pet care tasks."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def build_schedule(self):
        """Build a schedule for the owner's pets."""
        pass

    def sort_tasks(self, tasks):
        """Sort tasks using scheduling rules."""
        pass

    def filter_tasks(self, tasks, criteria: dict):
        """Filter tasks based on criteria."""
        pass

    def detect_conflicts(self, tasks):
        """Detect simple scheduling conflicts."""
        pass

    def explain_schedule(self, schedule):
        """Explain why tasks were placed in the schedule."""
        pass