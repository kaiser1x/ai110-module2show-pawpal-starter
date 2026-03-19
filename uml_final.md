```mermaid
classDiagram
    class Task {
        +str description
        +str due_date
        +str due_time
        +str frequency
        +bool completed
        +mark_complete() None
        +create_next_occurrence() Task
    }

    class Pet {
        +str name
        +str species
        +int age
        +List~Task~ tasks
        +add_task(task: Task) None
        +get_tasks() List~Task~
    }

    class Owner {
        +str name
        +List~Pet~ pets
        +add_pet(pet: Pet) None
        +get_pet(pet_name: str) Pet
        +get_all_tasks() List~Tuple~
    }

    class Scheduler {
        +Owner owner
        +get_tasks_for_date(date: str) List~Tuple~
        +sort_by_time(tasks) List~Tuple~
        +filter_tasks(tasks, pet_name, completed) List~Tuple~
        +detect_conflicts(tasks) List~str~
        +mark_task_complete(pet_name, task_description) bool
    }

    Owner "1" *-- "*" Pet : owns
    Pet "1" *-- "*" Task : stores
    Scheduler --> Owner : reads via get_all_tasks()
    Task ..> Task : create_next_occurrence()
```

## Changes from uml_draft.md

| Element | Draft | Final |
|---|---|---|
| `Task` attributes | `title`, `duration_minutes`, `priority`, `preferred_time` | `description`, `due_date`, `due_time`, `frequency` |
| `Task` methods | `mark_complete()` only | Added `create_next_occurrence()` |
| `Pet` attributes | had `preferences: dict` | Removed; added `age: int` |
| `Pet` methods | had `remove_task()` | Removed (not needed) |
| `Owner` methods | had `remove_pet()` | Removed; added `get_all_tasks()` |
| `Scheduler` methods | `build_schedule`, `sort_tasks`, `filter_tasks(criteria: dict)`, `explain_schedule` | `get_tasks_for_date`, `sort_by_time`, `filter_tasks(pet_name, completed)`, `detect_conflicts`, `mark_task_complete` |
| Relationship type | `-->` (association) | `*--` (composition) for Owner→Pet and Pet→Task; `-->` for Scheduler→Owner |
