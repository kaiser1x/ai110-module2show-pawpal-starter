from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup ---
owner = Owner(name="Alex")

# Pet 1: a dog
buddy = Pet(name="Buddy", species="Dog", age=3)
buddy.add_task(Task("Morning walk",      due_date="2026-03-18", due_time="07:00", frequency="daily"))
buddy.add_task(Task("Evening feeding",   due_date="2026-03-18", due_time="18:00", frequency="daily"))

# Pet 2: a cat
luna = Pet(name="Luna", species="Cat", age=5)
luna.add_task(Task("Litter box cleaning", due_date="2026-03-18", due_time="08:30", frequency="daily"))
luna.add_task(Task("Vet checkup",         due_date="2026-03-18", due_time="14:00", frequency="once"))

owner.add_pet(buddy)
owner.add_pet(luna)

# --- Scheduler ---
scheduler = Scheduler(owner)

TODAY = "2026-03-18"
todays_tasks = scheduler.get_tasks_for_date(TODAY)
sorted_tasks  = scheduler.sort_by_time(todays_tasks)
conflicts     = scheduler.detect_conflicts(todays_tasks)

# --- Display ---
print("=" * 48)
print(f"  PawPal+ | Today's Schedule — {TODAY}")
print("=" * 48)

for pet_name, task in sorted_tasks:
    status = "DONE" if task.completed else "TODO"
    repeat = f"({task.frequency})" if task.frequency != "once" else "(one-time)"
    print(f"  {task.due_time}  [{status}]  {pet_name} — {task.description}  {repeat}")

print("-" * 48)

if conflicts:
    print("  ⚠  Conflicts detected:")
    for warning in conflicts:
        print(f"     {warning}")
else:
    print("  No scheduling conflicts.")

print("=" * 48)
