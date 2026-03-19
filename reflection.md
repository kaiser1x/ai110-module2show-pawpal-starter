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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
