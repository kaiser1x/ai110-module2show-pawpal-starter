"""
PawPal+ demo — exercises every algorithm in pawpal_system.py:
  1. Sorting tasks by time (out-of-order input)
  2. Filtering by pet name and completion status
  3. Recurring tasks auto-scheduling next occurrence on mark_complete
  4. Conflict detection (two tasks at the exact same date + time)
"""

from pawpal_system import Task, Pet, Owner, Scheduler

# ── Helpers ────────────────────────────────────────────────────────────────

DIVIDER = "-" * 52

def print_tasks(label: str, task_pairs):
    """Pretty-print a labelled list of (pet_name, task) pairs."""
    print(f"\n{label}")
    print(DIVIDER)
    if not task_pairs:
        print("  (none)")
    for pet_name, task in task_pairs:
        status = "DONE" if task.completed else "TODO"
        repeat = f"({task.frequency})" if task.frequency != "once" else "(one-time)"
        print(f"  {task.due_time}  [{status}]  {pet_name} — {task.description}  {repeat}")
    print(DIVIDER)


# ── Setup ──────────────────────────────────────────────────────────────────

owner = Owner(name="Alex")

buddy = Pet(name="Buddy", species="Dog", age=3)
luna  = Pet(name="Luna",  species="Cat", age=5)

# Tasks added INTENTIONALLY out of order to prove sorting works
buddy.add_task(Task("Evening feeding",   due_date="2026-03-18", due_time="18:00", frequency="daily"))
buddy.add_task(Task("Morning walk",      due_date="2026-03-18", due_time="07:00", frequency="daily"))
buddy.add_task(Task("Midday water bowl", due_date="2026-03-18", due_time="12:00", frequency="daily"))

luna.add_task(Task("Litter box cleaning", due_date="2026-03-18", due_time="08:30", frequency="daily"))
luna.add_task(Task("Vet checkup",         due_date="2026-03-18", due_time="14:00", frequency="once"))

owner.add_pet(buddy)
owner.add_pet(luna)

scheduler = Scheduler(owner)
TODAY = "2026-03-18"

# ── Algorithm 1: Sorting ───────────────────────────────────────────────────
# Input order: 18:00 → 07:00 → 12:00 for Buddy; 08:30 → 14:00 for Luna
# Expected output order: 07:00 → 08:30 → 12:00 → 14:00 → 18:00

raw   = scheduler.get_tasks_for_date(TODAY)
sorted_tasks = scheduler.sort_by_time(raw)

print("\n" + "=" * 52)
print("  PawPal+  |  Algorithm Demo")
print("=" * 52)
print_tasks("1. SORTED by time (input was out of order)", sorted_tasks)

# ── Algorithm 2: Filtering ─────────────────────────────────────────────────

buddy_tasks = scheduler.filter_tasks(sorted_tasks, pet_name="Buddy")
print_tasks("2a. FILTERED — Buddy's tasks only", buddy_tasks)

luna_tasks = scheduler.filter_tasks(sorted_tasks, pet_name="Luna")
print_tasks("2b. FILTERED — Luna's tasks only", luna_tasks)

# Mark one task done so the completed filter has something to show
buddy.get_tasks()[1].mark_complete()   # marks "Morning walk" complete directly

completed_tasks = scheduler.filter_tasks(sorted_tasks, completed=True)
pending_tasks   = scheduler.filter_tasks(sorted_tasks, completed=False)
print_tasks("2c. FILTERED — completed tasks only", completed_tasks)
print_tasks("2d. FILTERED — pending tasks only",   pending_tasks)

# ── Algorithm 3: Recurring tasks ───────────────────────────────────────────
# mark_task_complete() marks done AND appends the next occurrence automatically

print("\n3. RECURRING TASKS — mark complete and auto-schedule next")
print(DIVIDER)

buddy_task_count_before = len(buddy.get_tasks())
result = scheduler.mark_task_complete("Buddy", "Midday water bowl")

buddy_task_count_after = len(buddy.get_tasks())
new_task = [t for t in buddy.get_tasks() if t.description == "Midday water bowl" and not t.completed][0]

print(f"  Tasks for Buddy before mark_complete: {buddy_task_count_before}")
print(f"  Tasks for Buddy after  mark_complete: {buddy_task_count_after}")
print(f"  Next occurrence added -> due: {new_task.due_date} at {new_task.due_time}")
print(DIVIDER)

# ── Algorithm 4: Conflict detection ───────────────────────────────────────
# Add two tasks at the exact same date + time to trigger a warning

print("\n4. CONFLICT DETECTION")
print(DIVIDER)

# First, show no conflicts in the original schedule
no_conflicts = scheduler.detect_conflicts(scheduler.get_tasks_for_date(TODAY))
print(f"  Conflicts in original schedule: {no_conflicts or 'none'}")

# Now deliberately create a conflict: add a second task for 08:30
buddy.add_task(Task("Morning brush", due_date="2026-03-18", due_time="08:30", frequency="once"))

conflict_check = scheduler.detect_conflicts(scheduler.get_tasks_for_date(TODAY))
print(f"\n  Added 'Morning brush' for Buddy at 08:30 (same as Luna's litter task)")
print(f"  Conflicts detected:")
for warning in conflict_check:
    print(f"    [!] {warning}")
print(DIVIDER)

print("\nAll algorithms verified.\n")
