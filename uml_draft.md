classDiagram
    class Owner {
        +str name
        +List~Pet~ pets
        +add_pet(pet: Pet)
        +remove_pet(pet: Pet)
        +get_pet(pet_name: str)
    }

    class Pet {
        +str name
        +str species
        +dict preferences
        +List~Task~ tasks
        +add_task(task: Task)
        +remove_task(task: Task)
        +get_tasks()
    }

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str preferred_time
        +bool completed
        +mark_complete()
    }

    class Scheduler {
        +Owner owner
        +build_schedule()
        +sort_tasks(tasks)
        +filter_tasks(tasks, criteria)
        +detect_conflicts(tasks)
        +explain_schedule(schedule)
    }

    Owner "1" --> "*" Pet : stores
    Pet "1" --> "*" Task : stores
    Scheduler --> Owner : builds schedule for