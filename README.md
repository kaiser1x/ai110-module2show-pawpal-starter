# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ goes beyond a plain task list with four scheduling algorithms built into the `Scheduler` class:

**Chronological sorting**
`sort_by_time()` orders any set of tasks from earliest to latest. It relies on the `"HH:MM"` time format being lexicographically ordered, so no date parsing is needed — a plain `sorted()` with a lambda key is enough.

**Flexible filtering**
`filter_tasks()` accepts an optional `pet_name` and an optional `completed` flag. Both filters compose: you can ask for "all of Luna's pending tasks today" in one call. Passing `None` for either parameter skips that filter entirely.

**Recurring task automation**
Tasks have a `frequency` field (`"once"`, `"daily"`, or `"weekly"`). When `mark_task_complete()` is called, it marks the task done *and* uses Python's `timedelta` to calculate the next due date, automatically appending a fresh copy to the pet's task list. The owner never has to re-enter a repeating task.

**Conflict detection**
`detect_conflicts()` scans a set of tasks and groups them by `(due_date, due_time)`. Any slot with two or more tasks produces a plain-English warning string (e.g. `"Conflict at 2026-03-18 08:30 — Buddy: Morning brush, Luna: Litter box cleaning"`). The method always returns warnings instead of raising exceptions, so the UI can display them gracefully.

---

## Testing PawPal+

### Run the tests

```bash
python -m pytest
```

All 38 tests should pass in under a second. No additional setup is required.

### What the tests cover

| Area | Happy-path tests | Edge-case tests |
|---|---|---|
| **Task** | starts incomplete, `mark_complete` changes status, idempotent double-complete | — |
| **Recurrence** | daily advances 1 day, weekly advances 7 days, next occurrence starts incomplete, preserves time & description | `once` returns `None`, weekly boundary date exact |
| **Pet** | add task increases count, `get_tasks` returns list | starts with zero tasks |
| **Owner** | `get_pet` returns correct pet, `get_all_tasks` returns tuples | case-insensitive name match, unknown name → `None` |
| **Sorting** | tasks returned in chronological order | single-task list, already-sorted input, reverse input |
| **Filtering** | filter by pet name, filter by completion status | empty input list, unknown pet name, combined pet + status filter |
| **Conflict detection** | two tasks at same slot produce one warning, no conflict when slots differ | three tasks in one slot (one warning), cross-pet same slot, two distinct slots |
| **Scheduler.mark_task_complete** | marks done, appends next occurrence, `once` adds no new task | unknown pet returns `False` |

### Confidence level

★★★★☆ (4 / 5)

The core scheduling logic — sorting, filtering, recurrence, and conflict detection — is fully tested across both happy paths and realistic edge cases. One star is withheld because the conflict detector only checks for **exact time matches**, not overlapping durations (a known tradeoff documented in `reflection.md §2b`). Adding a `duration_minutes` field in a future iteration would require new tests for that overlap logic.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
