import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet care scheduler — sort, filter, detect conflicts, and automate recurring tasks.")

# ── Session-state vault ─────────────────────────────────────────────────────
# The Owner object is created once and stored here so it survives re-runs.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="")

owner: Owner = st.session_state.owner


# ── Sidebar: Owner & pet management ────────────────────────────────────────
with st.sidebar:
    st.header("👤 Owner")
    owner_name = st.text_input("Your name", value=owner.name or "")
    if owner_name and owner_name != owner.name:
        owner.name = owner_name

    st.divider()
    st.subheader("🐕 Add a Pet")

    with st.form("add_pet_form", clear_on_submit=True):
        new_pet_name    = st.text_input("Pet name")
        new_pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
        new_pet_age     = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
        add_pet_btn     = st.form_submit_button("Add pet", use_container_width=True)

    if add_pet_btn:
        if not new_pet_name.strip():
            st.sidebar.warning("Please enter a pet name.")
        elif owner.get_pet(new_pet_name):
            st.sidebar.warning(f"'{new_pet_name}' is already in your list.")
        else:
            owner.add_pet(Pet(name=new_pet_name.strip(), species=new_pet_species, age=int(new_pet_age)))
            st.sidebar.success(f"✅ {new_pet_name} added!")

    # Pet roster
    if owner.pets:
        st.markdown("**Your pets:**")
        for p in owner.pets:
            task_count = len(p.get_tasks())
            st.write(f"- **{p.name}** ({p.species}, age {p.age}) — {task_count} task(s)")
    else:
        st.info("No pets yet. Add one above.")


# ── Main area: tabs ─────────────────────────────────────────────────────────
tab_schedule, tab_add_task, tab_complete = st.tabs(
    ["📅 Schedule", "➕ Add Task", "✅ Mark Complete"]
)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 1: Schedule — sorted, filtered, conflict-aware
# ══════════════════════════════════════════════════════════════════════════════
with tab_schedule:
    st.subheader("Daily Schedule")

    if not owner.pets:
        st.info("Add a pet in the sidebar to get started.")
    else:
        selected_date     = st.date_input("View schedule for", value=date.today())
        selected_date_str = str(selected_date)

        scheduler    = Scheduler(owner)
        tasks_today  = scheduler.get_tasks_for_date(selected_date_str)
        sorted_tasks = scheduler.sort_by_time(tasks_today)   # Algorithm: chronological sort
        conflicts    = scheduler.detect_conflicts(tasks_today) # Algorithm: conflict detection

        # ── Summary metrics ────────────────────────────────────────────────
        total     = len(sorted_tasks)
        done      = sum(1 for _, t in sorted_tasks if t.completed)
        pending   = total - done

        m1, m2, m3 = st.columns(3)
        m1.metric("Total tasks", total)
        m2.metric("Pending", pending)
        m3.metric("Completed", done)

        # ── Conflict warnings — shown prominently above the task list ──────
        if conflicts:
            st.error(
                "**Scheduling conflicts detected** — two or more tasks share the same time slot. "
                "Consider rescheduling one of the tasks below."
            )
            for warning in conflicts:
                # Parse the conflict string to highlight it clearly
                st.warning(f"⏰ {warning}", icon="⚠️")
        elif total > 0:
            st.success("No scheduling conflicts for this day.", icon="✅")

        st.divider()

        if not sorted_tasks:
            st.info(f"No tasks scheduled for {selected_date_str}.")
        else:
            # ── Filter controls ────────────────────────────────────────────
            col_pet, col_status = st.columns(2)
            with col_pet:
                pet_names  = ["All pets"] + [p.name for p in owner.pets]
                filter_pet = st.selectbox("Filter by pet", pet_names, label_visibility="visible")
            with col_status:
                filter_done = st.radio("Status", ["All", "Pending", "Completed"], horizontal=True)

            # Algorithm: filter_tasks composes both filters in one call
            filtered = sorted_tasks
            if filter_pet != "All pets":
                filtered = scheduler.filter_tasks(filtered, pet_name=filter_pet)
            if filter_done == "Pending":
                filtered = scheduler.filter_tasks(filtered, completed=False)
            elif filter_done == "Completed":
                filtered = scheduler.filter_tasks(filtered, completed=True)

            st.caption(f"Showing {len(filtered)} of {total} task(s), sorted by time.")

            # ── Task cards ─────────────────────────────────────────────────
            for pet_name, task in filtered:
                with st.container(border=True):
                    col_icon, col_info, col_badge = st.columns([1, 6, 2])

                    with col_icon:
                        st.markdown("✅" if task.completed else "🔲")

                    with col_info:
                        st.markdown(f"**{task.due_time}** &nbsp;|&nbsp; **{pet_name}** — {task.description}")

                    with col_badge:
                        if task.frequency == "once":
                            st.caption("one-time")
                        elif task.frequency == "daily":
                            st.caption("🔁 daily")
                        else:
                            st.caption("🔁 weekly")


# ══════════════════════════════════════════════════════════════════════════════
# Tab 2: Add Task
# ══════════════════════════════════════════════════════════════════════════════
with tab_add_task:
    st.subheader("Schedule a New Task")

    if not owner.pets:
        st.info("Add a pet in the sidebar first.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            target_pet  = st.selectbox("Pet", [p.name for p in owner.pets])
            description = st.text_input("Task description", placeholder="e.g. Morning walk")

            col_date, col_time = st.columns(2)
            with col_date:
                due_date = st.date_input("Due date", value=date.today())
            with col_time:
                due_time = st.time_input("Due time")

            frequency    = st.selectbox(
                "Frequency",
                ["once", "daily", "weekly"],
                help="Daily and weekly tasks auto-schedule the next occurrence when marked complete."
            )
            add_task_btn = st.form_submit_button("Add task", use_container_width=True)

        if add_task_btn:
            if not description.strip():
                st.warning("Please enter a task description.")
            else:
                pet = owner.get_pet(target_pet)
                new_task = Task(
                    description=description.strip(),
                    due_date=str(due_date),
                    due_time=due_time.strftime("%H:%M"),
                    frequency=frequency,
                )
                pet.add_task(new_task)

                # Check immediately if this new task conflicts with existing ones
                scheduler     = Scheduler(owner)
                day_tasks     = scheduler.get_tasks_for_date(str(due_date))
                new_conflicts = scheduler.detect_conflicts(day_tasks)

                st.success(
                    f"Added **'{description}'** for **{target_pet}** "
                    f"on {due_date} at {due_time.strftime('%H:%M')} ({frequency})."
                )
                if new_conflicts:
                    st.warning(
                        "This task creates a time conflict. "
                        "Check the Schedule tab for details.",
                        icon="⚠️"
                    )


# ══════════════════════════════════════════════════════════════════════════════
# Tab 3: Mark Complete — shows next occurrence info for recurring tasks
# ══════════════════════════════════════════════════════════════════════════════
with tab_complete:
    st.subheader("Mark a Task as Complete")

    if not owner.pets:
        st.info("Add a pet in the sidebar first.")
    else:
        scheduler = Scheduler(owner)

        col_pet, col_date = st.columns(2)
        with col_pet:
            chosen_pet  = st.selectbox("Pet", [p.name for p in owner.pets], key="complete_pet")
        with col_date:
            chosen_date = st.date_input("Date", value=date.today(), key="complete_date")

        tasks_on_date = scheduler.get_tasks_for_date(str(chosen_date))
        pending       = scheduler.filter_tasks(tasks_on_date, pet_name=chosen_pet, completed=False)

        if not pending:
            st.info(f"No pending tasks for **{chosen_pet}** on {chosen_date}.")
        else:
            task_labels = [t.description for _, t in pending]
            chosen_desc = st.selectbox("Task to complete", task_labels)

            # Preview the chosen task's recurrence before the button is clicked
            chosen_task = next((t for _, t in pending if t.description == chosen_desc), None)
            if chosen_task and chosen_task.frequency != "once":
                st.info(
                    f"This is a **{chosen_task.frequency}** task. "
                    "Marking it complete will automatically schedule the next occurrence.",
                    icon="🔁"
                )

            if st.button("Mark complete", use_container_width=True):
                success = scheduler.mark_task_complete(chosen_pet, chosen_desc)
                if success:
                    pet = owner.get_pet(chosen_pet)
                    # Find the newly-added next occurrence (not yet complete)
                    next_occurrence = next(
                        (t for t in pet.get_tasks()
                         if t.description == chosen_desc and not t.completed),
                        None
                    )
                    if next_occurrence:
                        st.success(
                            f"✅ **'{chosen_desc}'** marked complete!  \n"
                            f"Next occurrence scheduled for **{next_occurrence.due_date}** "
                            f"at **{next_occurrence.due_time}**."
                        )
                    else:
                        st.success(f"✅ **'{chosen_desc}'** marked complete!")
                else:
                    st.error("Could not find that task. It may already be complete.")
