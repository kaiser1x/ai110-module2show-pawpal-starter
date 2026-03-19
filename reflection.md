# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design for PawPal+ focused on three main user actions: entering owner and pet information, adding pet care tasks with scheduling details, and generating a daily care schedule. Since the starter UI already includes inputs for an owner, a pet, task duration, and task priority, I designed the system around four main classes: Owner, Pet, Task, and Scheduler.

The Owner class represents the person using the app and stores basic information along with the pets they manage. The Pet class represents an individual animal and stores details such as name, species, and its care tasks. The Task class represents one care activity, such as a walk or feeding, and stores information like the task title, duration, priority, preferred time, and completion status. The Scheduler class is responsible for building an ordered daily schedule by considering the task information and applying simple scheduling rules such as sorting and prioritization.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

My design changed slightly after reviewing the starter Streamlit app. At first, I planned a simpler task model based mostly on due dates and times, but the UI and project description emphasized duration, priority, and scheduling constraints. Because of that, I adjusted the Task design to include duration and priority as core attributes, and I kept the Scheduler focused on creating an ordered plan for the day instead of only listing tasks. This made the design fit the actual user interface and project goals more closely.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The Scheduler considers three constraints: due date (tasks are only surfaced for the date you request), due time (tasks are sorted chronologically within that date), and completion status (completed tasks can be hidden so the owner sees only what still needs doing). Frequency is also a constraint in the sense that recurring tasks self-extend when marked complete.

I prioritised time-based ordering first because a pet owner's day is fundamentally sequential — knowing that the morning walk comes before the midday feeding is more immediately useful than knowing its priority level. Completion status came second because an owner scanning a busy day needs to skip over things already done.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The conflict detector only flags tasks that share the **exact same date and time string** (e.g., two tasks both at `08:30`). It does not check for *overlapping* durations — for example, a 60-minute walk starting at `08:00` would not conflict with a task starting at `08:30`, even though they would overlap in real life.

This tradeoff is reasonable for a beginner-level system because tasks in PawPal+ do not yet store a duration, so there is no reliable way to compute overlap. An exact-match check is simple, correct for the data model we have, and produces clear warning messages without crashing. If a `duration_minutes` field were added later, the conflict check could be upgraded to compare start-to-end intervals — but adding that complexity now would over-engineer a system that does not yet need it.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI assistance across every phase of this project, but with a different purpose at each stage. During design, I used it to brainstorm which class responsibilities made sense — for example, asking whether conflict detection belonged in `Task`, `Pet`, or `Scheduler`. During implementation, I used inline prompts to generate method bodies and then read them carefully before accepting. During testing, I asked it to suggest edge cases I might have missed, such as an owner with no pets or a filter applied to an already-empty list.

The most effective Copilot features were **inline chat on specific methods** and **the Generate Tests smart action**. Asking a focused question like "suggest a key parameter for sorting HH:MM strings" produced a clean, immediately usable answer. Broad questions like "write my whole scheduler" produced suggestions that had to be significantly reworked, because the AI could not know the exact interface I had already designed for `get_all_tasks()`.

The most useful prompt pattern throughout the project was giving the AI a constraint alongside the request: "write a filter method that takes optional parameters so None means no filter applied." That constraint produced code that matched my design rather than code I had to reshape to fit it.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I asked for help with the initial class skeleton, the AI suggested storing a flat list of tasks directly inside `Scheduler` as a shortcut, so the scheduler would own its own copy of the task data rather than reading through `Owner → Pet → Task`. I rejected this because it would have created two sources of truth — one inside `Scheduler` and one inside each `Pet`. If a task were marked complete through the `Pet` object, the `Scheduler`'s copy would not reflect the change, and the UI would show stale data.

I verified my instinct by tracing the data flow: the `Owner` already has `get_all_tasks()`, which walks every pet and collects their tasks live. Any method that calls `get_all_tasks()` always sees the current state. I kept `Scheduler` as a stateless layer that reads through `Owner` rather than storing anything itself, which is the design principle documented in the original spec.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The test suite covers 38 behaviors across all four classes. The most important groups were:

- **Recurrence** — verifying that `create_next_occurrence()` produces exactly the right date (`+1 day` or `+7 days`) and that the new task starts with `completed=False`. This is the feature most likely to produce subtle bugs because it involves date arithmetic.
- **Sorting** — testing not just that sorted output is ordered, but that reverse-order input is also corrected. A sort that only works on already-sorted input would not be caught by a single test.
- **Conflict detection** — testing cross-pet conflicts (two different animals at the same time) separately from same-pet conflicts, because the grouping logic treats both the same way but they represent different real-world problems.
- **Edge cases** — empty pet lists, empty task lists, unknown pet names, and filters that return zero results. These mattered because the Streamlit UI calls these methods on every page render, so any crash on an empty state would break the app for a new user who has not added any data yet.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident (4/5) that the core scheduling logic is correct. The one honest gap is duration-overlap detection: two tasks that start at different times but whose durations overlap are not flagged as conflicts. This is a known and documented tradeoff rather than an oversight, but it means the conflict detection is incomplete for real-world use.

If I had more time, the next tests I would write are:
- A task added with a `due_date` in a past year should still appear when that date is queried (verifying no date validation blocks historical entries)
- Calling `mark_task_complete` twice on the same recurring task should add two separate next occurrences, not overwrite one
- A pet with 100+ tasks should still sort and filter in the correct order (basic scale test)

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part I am most satisfied with is the clean separation between the logic layer (`pawpal_system.py`) and the UI layer (`app.py`). Because `Scheduler` is stateless and reads all data through `Owner`, the entire backend can be tested independently in `main.py` or `pytest` without running Streamlit at all. This made debugging much faster — when something looked wrong in the UI, I could reproduce and fix it in the terminal first, then confirm the fix appeared in the browser. The 38-test suite passing in under one second is a direct result of keeping the logic layer free of any UI dependencies.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would add a `duration_minutes` field to `Task` and upgrade `detect_conflicts()` to compare time intervals instead of exact start times. This is the single biggest gap between the current system and real-world usefulness. I would also add data persistence — currently all pets and tasks are lost when the browser tab is closed. A simple JSON file or SQLite database would let the owner's schedule survive between sessions without adding much complexity to the class design.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that **the AI is a fast executor, but a poor architect**. It can generate a working method body in seconds, but it does not know what interface that method needs to fit, what other methods will call it, or what tradeoffs you have already decided on. Every time I gave the AI a precise constraint — a specific return type, a specific parameter signature, a specific design rule — the output was useful immediately. Every time I asked an open-ended question without those constraints, I spent more time editing the suggestion than I would have spent writing the code myself.

Being the "lead architect" means making those decisions first, documenting them clearly (in docstrings, in the UML, in this reflection), and then using AI to fill in the implementation details within the boundaries you have set. The architect's job does not shrink when AI is in the room — it becomes more important, because someone has to decide which of the AI's many possible solutions is actually the right one for this specific system.
