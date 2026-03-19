from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


@dataclass
class Task:
    """Represents a single pet care activity with scheduling info."""

    description: str
    due_date: str        # "YYYY-MM-DD"
    due_time: str        # "HH:MM"
    frequency: str       # "once", "daily", or "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def create_next_occurrence(self) -> Optional["Task"]:
        """Return a new Task for the next occurrence, or None if frequency is 'once'."""
        if self.frequency == "once":
            return None

        current_date = datetime.strptime(self.due_date, "%Y-%m-%d")

        if self.frequency == "daily":
            next_date = current_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = current_date + timedelta(weeks=1)
        else:
            return None

        return Task(
            description=self.description,
            due_date=next_date.strftime("%Y-%m-%d"),
            due_time=self.due_time,
            frequency=self.frequency,
            completed=False,
        )


@dataclass
class Pet:
    """Represents a pet and its associated care tasks."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks


@dataclass
class Owner:
    """Represents a pet owner who manages one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to the owner's list."""
        self.pets.append(pet)

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return the Pet matching pet_name (case-insensitive), or None if not found."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        """Return all tasks across every pet as a list of (pet_name, task) tuples."""
        result = []
        for pet in self.pets:
            for task in pet.get_tasks():
                result.append((pet.name, task))
        return result


class Scheduler:
    """Main logic layer that organizes and manages tasks across all pets for an owner."""

    def __init__(self, owner: Owner):
        """Initialize the Scheduler with an Owner whose pets and tasks it will manage."""
        self.owner = owner

    def get_tasks_for_date(self, date: str) -> List[Tuple[str, Task]]:
        """Return all (pet_name, task) pairs where the task's due_date matches date."""
        return [
            (pet_name, task)
            for pet_name, task in self.owner.get_all_tasks()
            if task.due_date == date
        ]

    def sort_by_time(self, tasks: List[Tuple[str, Task]]) -> List[Tuple[str, Task]]:
        """Return a new list of tasks sorted chronologically by due_time.

        Sorting works correctly on plain "HH:MM" strings because that format
        is lexicographically ordered (e.g. "07:00" < "08:30" < "18:00").

        Args:
            tasks: A list of (pet_name, Task) tuples to sort.

        Returns:
            A new list with the same tuples ordered earliest to latest.
        """
        return sorted(tasks, key=lambda pair: pair[1].due_time)

    def filter_tasks(
        self,
        tasks: List[Tuple[str, Task]],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Tuple[str, Task]]:
        """Return a filtered subset of tasks based on pet name and/or completion status.

        Both filters are optional and compose — passing both narrows the result
        to tasks that satisfy each condition. Passing neither returns the original
        list unchanged.

        Args:
            tasks:     A list of (pet_name, Task) tuples to filter.
            pet_name:  If provided, keep only tasks belonging to this pet
                       (case-insensitive). Pass None to skip this filter.
            completed: If True, keep only completed tasks. If False, keep only
                       pending tasks. Pass None to skip this filter.

        Returns:
            A new list containing only the tuples that pass every active filter.
        """
        result = tasks

        if pet_name is not None:
            result = [
                (pn, t) for pn, t in result
                if pn.lower() == pet_name.lower()
            ]

        if completed is not None:
            result = [
                (pn, t) for pn, t in result
                if t.completed == completed
            ]

        return result

    def detect_conflicts(self, tasks: List[Tuple[str, Task]]) -> List[str]:
        """Detect scheduling conflicts and return human-readable warning messages.

        Two or more tasks are considered a conflict when they share the exact
        same due_date and due_time string. Duration overlap is not checked
        (see reflection.md §2b for the tradeoff reasoning).

        Args:
            tasks: A list of (pet_name, Task) tuples to inspect.

        Returns:
            A list of warning strings, one per conflicting time slot.
            Returns an empty list when no conflicts are found.
            Example warning: "Conflict at 2026-03-18 08:30 — Buddy: Morning brush, Luna: Litter box cleaning"
        """
        seen: dict = {}  # key: (due_date, due_time) -> list of (pet_name, description)
        for pet_name, task in tasks:
            key = (task.due_date, task.due_time)
            seen.setdefault(key, []).append(f"{pet_name}: {task.description}")

        warnings = []
        for (date, time), entries in seen.items():
            if len(entries) > 1:
                conflict_list = ", ".join(entries)
                warnings.append(
                    f"Conflict at {date} {time} — {conflict_list}"
                )
        return warnings

    def mark_task_complete(self, pet_name: str, task_description: str) -> bool:
        """Mark the first matching incomplete task done and auto-schedule the next occurrence.

        Searches the named pet's task list for the first incomplete task whose
        description matches (case-insensitive). If found, it is marked complete
        and — for daily or weekly tasks — a new Task is appended to the pet's
        list with the next calculated due_date (today + 1 day or + 7 days).

        Args:
            pet_name:         Name of the pet whose task should be marked done
                              (case-insensitive).
            task_description: Description of the task to mark complete
                              (case-insensitive, matches the first incomplete
                              occurrence only).

        Returns:
            True  if a matching incomplete task was found and marked.
            False if the pet does not exist or no matching incomplete task was found.
        """
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return False

        for task in pet.get_tasks():
            if (
                task.description.lower() == task_description.lower()
                and not task.completed
            ):
                task.mark_complete()
                next_task = task.create_next_occurrence()
                if next_task is not None:
                    pet.add_task(next_task)
                return True

        return False
