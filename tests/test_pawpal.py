import sys
import os

# Allow imports from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler


# ── Fixtures (reusable test data) ──────────────────────────────────────────

def make_task(description="Feed cat", due_date="2026-03-18", due_time="08:00", frequency="once"):
    """Return a basic Task for use in tests."""
    return Task(description=description, due_date=due_date, due_time=due_time, frequency=frequency)


def make_pet(name="Luna", species="Cat", age=2):
    """Return a Pet with no tasks."""
    return Pet(name=name, species=species, age=age)


# ── Task tests ─────────────────────────────────────────────────────────────

def test_task_starts_incomplete():
    """A new task should have completed=False by default."""
    task = make_task()
    assert task.completed is False


def test_mark_complete_changes_status():
    """Calling mark_complete() should set completed to True."""
    task = make_task()
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_is_idempotent():
    """Calling mark_complete() twice should not raise and should stay True."""
    task = make_task()
    task.mark_complete()
    task.mark_complete()
    assert task.completed is True


# ── Recurring task tests ───────────────────────────────────────────────────

def test_create_next_occurrence_once_returns_none():
    """frequency='once' tasks should return None for next occurrence."""
    task = make_task(frequency="once")
    assert task.create_next_occurrence() is None


def test_create_next_occurrence_daily_advances_one_day():
    """frequency='daily' should produce a task dated one day later."""
    task = make_task(due_date="2026-03-18", frequency="daily")
    next_task = task.create_next_occurrence()
    assert next_task is not None
    assert next_task.due_date == "2026-03-19"


def test_create_next_occurrence_weekly_advances_seven_days():
    """frequency='weekly' should produce a task dated seven days later."""
    task = make_task(due_date="2026-03-18", frequency="weekly")
    next_task = task.create_next_occurrence()
    assert next_task is not None
    assert next_task.due_date == "2026-03-25"


def test_create_next_occurrence_is_not_completed():
    """The next occurrence should always start as incomplete."""
    task = make_task(frequency="daily")
    task.mark_complete()
    next_task = task.create_next_occurrence()
    assert next_task.completed is False


# ── Pet tests ──────────────────────────────────────────────────────────────

def test_pet_starts_with_no_tasks():
    """A freshly created pet should have an empty task list."""
    pet = make_pet()
    assert len(pet.get_tasks()) == 0


def test_add_task_increases_count():
    """Adding a task to a pet should increase its task count by one."""
    pet = make_pet()
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1


def test_add_multiple_tasks():
    """Adding three tasks should result in a task list of length three."""
    pet = make_pet()
    for i in range(3):
        pet.add_task(make_task(description=f"Task {i}"))
    assert len(pet.get_tasks()) == 3


# ── Owner tests ────────────────────────────────────────────────────────────

def test_get_pet_returns_correct_pet():
    """get_pet() should return the pet with the matching name."""
    owner = Owner(name="Alex")
    owner.add_pet(make_pet(name="Buddy"))
    found = owner.get_pet("Buddy")
    assert found is not None
    assert found.name == "Buddy"


def test_get_pet_is_case_insensitive():
    """get_pet() should match regardless of letter case."""
    owner = Owner(name="Alex")
    owner.add_pet(make_pet(name="Luna"))
    assert owner.get_pet("luna") is not None
    assert owner.get_pet("LUNA") is not None


def test_get_pet_returns_none_for_unknown_name():
    """get_pet() should return None when no pet matches the given name."""
    owner = Owner(name="Alex")
    assert owner.get_pet("Ghost") is None


def test_get_all_tasks_returns_tuples():
    """get_all_tasks() should return (pet_name, task) tuples for every task."""
    owner = Owner(name="Alex")
    pet = make_pet(name="Buddy")
    task = make_task()
    pet.add_task(task)
    owner.add_pet(pet)

    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 1
    pet_name, returned_task = all_tasks[0]
    assert pet_name == "Buddy"
    assert returned_task is task


# ── Scheduler tests ────────────────────────────────────────────────────────

def _build_owner():
    """Return a pre-populated Owner for Scheduler tests."""
    owner = Owner(name="Alex")

    buddy = make_pet(name="Buddy", species="Dog")
    buddy.add_task(Task("Morning walk",    "2026-03-18", "07:00", "daily"))
    buddy.add_task(Task("Evening feeding", "2026-03-18", "18:00", "daily"))

    luna = make_pet(name="Luna", species="Cat")
    luna.add_task(Task("Litter cleaning",  "2026-03-18", "08:30", "daily"))
    luna.add_task(Task("Vet visit",        "2026-03-19", "09:00", "once"))

    owner.add_pet(buddy)
    owner.add_pet(luna)
    return owner


def test_get_tasks_for_date_returns_matching_tasks():
    """get_tasks_for_date() should only return tasks on the given date."""
    s = Scheduler(_build_owner())
    tasks = s.get_tasks_for_date("2026-03-18")
    assert len(tasks) == 3  # walk, feeding, litter — not the vet visit on 03-19


def test_get_tasks_for_date_excludes_other_dates():
    """Tasks on a different date should not appear in the result."""
    s = Scheduler(_build_owner())
    tasks = s.get_tasks_for_date("2026-03-20")
    assert len(tasks) == 0


def test_sort_by_time_orders_chronologically():
    """sort_by_time() should order tasks earliest to latest."""
    s = Scheduler(_build_owner())
    tasks = s.get_tasks_for_date("2026-03-18")
    sorted_tasks = s.sort_by_time(tasks)
    times = [t.due_time for _, t in sorted_tasks]
    assert times == sorted(times)


def test_filter_by_pet_name():
    """filter_tasks(pet_name=...) should return only that pet's tasks."""
    s = Scheduler(_build_owner())
    tasks = s.get_tasks_for_date("2026-03-18")
    buddy_tasks = s.filter_tasks(tasks, pet_name="Buddy")
    assert all(pn == "Buddy" for pn, _ in buddy_tasks)
    assert len(buddy_tasks) == 2


def test_filter_by_completed_status():
    """filter_tasks(completed=False) should exclude completed tasks."""
    s = Scheduler(_build_owner())
    tasks = s.get_tasks_for_date("2026-03-18")
    # Mark one task complete so we have a mix
    tasks[0][1].mark_complete()
    incomplete = s.filter_tasks(tasks, completed=False)
    assert all(not t.completed for _, t in incomplete)


def test_detect_conflicts_found():
    """detect_conflicts() should flag tasks with identical date and time."""
    owner = Owner(name="Alex")
    pet = make_pet()
    pet.add_task(Task("Task A", "2026-03-18", "09:00", "once"))
    pet.add_task(Task("Task B", "2026-03-18", "09:00", "once"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    tasks = s.get_tasks_for_date("2026-03-18")
    warnings = s.detect_conflicts(tasks)
    assert len(warnings) == 1
    assert "09:00" in warnings[0]


def test_detect_conflicts_none():
    """detect_conflicts() should return an empty list when no conflicts exist."""
    s = Scheduler(_build_owner())
    tasks = s.get_tasks_for_date("2026-03-18")
    assert s.detect_conflicts(tasks) == []


def test_mark_task_complete_marks_done():
    """mark_task_complete() should set the matching task's completed flag."""
    s = Scheduler(_build_owner())
    result = s.mark_task_complete("Buddy", "Morning walk")
    assert result is True
    pet = s.owner.get_pet("Buddy")
    done = [t for t in pet.get_tasks() if t.description == "Morning walk" and t.completed]
    assert len(done) == 1


def test_mark_task_complete_adds_next_occurrence():
    """Completing a recurring task should append the next occurrence to the pet."""
    s = Scheduler(_build_owner())
    pet = s.owner.get_pet("Buddy")
    count_before = len(pet.get_tasks())
    s.mark_task_complete("Buddy", "Morning walk")
    assert len(pet.get_tasks()) == count_before + 1


def test_mark_task_complete_once_no_next_occurrence():
    """Completing a 'once' task should NOT add a new task."""
    owner = Owner(name="Alex")
    pet = make_pet()
    pet.add_task(Task("Vet visit", "2026-03-18", "14:00", "once"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.mark_task_complete("Luna", "Vet visit")
    assert len(pet.get_tasks()) == 1  # no new task added


def test_mark_task_complete_unknown_pet_returns_false():
    """mark_task_complete() should return False for a pet that doesn't exist."""
    s = Scheduler(_build_owner())
    assert s.mark_task_complete("Ghost", "Some task") is False
