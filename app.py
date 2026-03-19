import streamlit as st
from datetime import date

# Step 1: Import the classes from our logic layer
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Step 2: Session-state "vault" ──────────────────────────────────────────
# st.session_state works like a dictionary that survives re-runs.
# We only create the Owner once; every subsequent re-run finds it already here.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="")

owner: Owner = st.session_state.owner


# ── Sidebar: Owner setup ───────────────────────────────────────────────────
with st.sidebar:
    st.header("Owner")
    owner_name = st.text_input("Your name", value=owner.name or "")
    if owner_name and owner_name != owner.name:
        owner.name = owner_name   # update in-place; session_state keeps the ref

    st.divider()

    # ── Add a pet ──────────────────────────────────────────────────────────
    st.subheader("Add a Pet")
    with st.form("add_pet_form", clear_on_submit=True):
        new_pet_name    = st.text_input("Pet name")
        new_pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
        new_pet_age     = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
        add_pet_btn     = st.form_submit_button("Add pet")

    # Step 3: Wire the form submit to owner.add_pet()
    if add_pet_btn:
        if not new_pet_name.strip():
            st.sidebar.warning("Please enter a pet name.")
        elif owner.get_pet(new_pet_name):
            st.sidebar.warning(f"'{new_pet_name}' is already in your list.")
        else:
            # This is the bridge: UI data → Pet object → owner.add_pet()
            owner.add_pet(Pet(name=new_pet_name.strip(), species=new_pet_species, age=int(new_pet_age)))
            st.sidebar.success(f"{new_pet_name} added!")

    # Show current pets in sidebar
    if owner.pets:
        st.markdown("**Your pets:**")
        for p in owner.pets:
            st.write(f"- {p.name} ({p.species}, age {p.age})")
    else:
        st.info("No pets yet.")


# ── Main area: tabs ────────────────────────────────────────────────────────
tab_schedule, tab_add_task, tab_complete = st.tabs(
    ["📅 Today's Schedule", "➕ Add Task", "✅ Mark Complete"]
)


# ── Tab 1: Today's Schedule ────────────────────────────────────────────────
with tab_schedule:
    st.subheader("Today's Schedule")

    today_str = str(date.today())          # "YYYY-MM-DD"
    selected_date = st.date_input("View schedule for", value=date.today())
    selected_date_str = str(selected_date)

    if not owner.pets:
        st.info("Add a pet in the sidebar to get started.")
    else:
        scheduler = Scheduler(owner)
        tasks_today = scheduler.get_tasks_for_date(selected_date_str)
        sorted_tasks = scheduler.sort_by_time(tasks_today)
        conflicts    = scheduler.detect_conflicts(tasks_today)

        # Conflict warnings
        if conflicts:
            for warning in conflicts:
                st.warning(f"⚠ {warning}")

        if not sorted_tasks:
            st.info(f"No tasks scheduled for {selected_date_str}.")
        else:
            # Filter controls
            pet_names   = ["All"] + [p.name for p in owner.pets]
            filter_pet  = st.selectbox("Filter by pet", pet_names)
            filter_done = st.radio("Show", ["All", "Pending", "Completed"], horizontal=True)

            filtered = sorted_tasks
            if filter_pet != "All":
                filtered = scheduler.filter_tasks(filtered, pet_name=filter_pet)
            if filter_done == "Pending":
                filtered = scheduler.filter_tasks(filtered, completed=False)
            elif filter_done == "Completed":
                filtered = scheduler.filter_tasks(filtered, completed=True)

            # Render each task as a card-style row
            for pet_name, task in filtered:
                status_icon = "✅" if task.completed else "🔲"
                repeat_label = f"({task.frequency})" if task.frequency != "once" else "(one-time)"
                st.markdown(
                    f"{status_icon} &nbsp; **{task.due_time}** &nbsp;|&nbsp; "
                    f"**{pet_name}** — {task.description} &nbsp; `{repeat_label}`"
                )

            st.caption(f"{len(filtered)} task(s) shown.")


# ── Tab 2: Add a Task ──────────────────────────────────────────────────────
with tab_add_task:
    st.subheader("Schedule a New Task")

    if not owner.pets:
        st.info("Add a pet in the sidebar first.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            target_pet   = st.selectbox("Pet", [p.name for p in owner.pets])
            description  = st.text_input("Task description", placeholder="e.g. Morning walk")
            due_date     = st.date_input("Due date", value=date.today())
            due_time     = st.time_input("Due time")
            frequency    = st.selectbox("Frequency", ["once", "daily", "weekly"])
            add_task_btn = st.form_submit_button("Add task")

        # Step 3: Wire form submit → Task object → pet.add_task()
        if add_task_btn:
            if not description.strip():
                st.warning("Please enter a task description.")
            else:
                pet = owner.get_pet(target_pet)    # Owner looks up the Pet
                new_task = Task(
                    description=description.strip(),
                    due_date=str(due_date),                    # "YYYY-MM-DD"
                    due_time=due_time.strftime("%H:%M"),       # "HH:MM"
                    frequency=frequency,
                )
                pet.add_task(new_task)             # Pet stores the Task
                st.success(
                    f"Added '{description}' for {target_pet} on {due_date} at {due_time.strftime('%H:%M')}."
                )


# ── Tab 3: Mark a Task Complete ────────────────────────────────────────────
with tab_complete:
    st.subheader("Mark a Task as Complete")

    if not owner.pets:
        st.info("Add a pet in the sidebar first.")
    else:
        scheduler = Scheduler(owner)

        col_pet, col_date = st.columns(2)
        with col_pet:
            chosen_pet = st.selectbox("Pet", [p.name for p in owner.pets], key="complete_pet")
        with col_date:
            chosen_date = st.date_input("Date", value=date.today(), key="complete_date")

        # Show only pending tasks for that pet/date so the user can pick one
        tasks_on_date = scheduler.get_tasks_for_date(str(chosen_date))
        pending = scheduler.filter_tasks(tasks_on_date, pet_name=chosen_pet, completed=False)

        if not pending:
            st.info("No pending tasks for this pet on the selected date.")
        else:
            task_labels = [t.description for _, t in pending]
            chosen_desc = st.selectbox("Task to complete", task_labels)

            if st.button("Mark complete"):
                # Step 3: Bridge — Scheduler finds the task and calls mark_complete()
                success = scheduler.mark_task_complete(chosen_pet, chosen_desc)
                if success:
                    # Check if a next occurrence was created
                    pet = owner.get_pet(chosen_pet)
                    recurring_added = any(
                        t.description == chosen_desc and not t.completed
                        for t in pet.get_tasks()
                    )
                    msg = f"✅ '{chosen_desc}' marked complete!"
                    if recurring_added:
                        msg += " Next occurrence has been scheduled."
                    st.success(msg)
                else:
                    st.error("Could not find that task. It may already be complete.")
