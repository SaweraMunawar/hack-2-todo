# Phase I Implementation Tasks

## Status Overview

| Category | Status | Notes |
|----------|--------|-------|
| Project Setup | ✅ Complete | Git, UV, structure ready |
| Specifications | ✅ Complete | 11 spec files created |
| Source Code | ⬜ Pending | Skeleton only |
| Tests | ⬜ Pending | Not started |
| Demo Video | ⬜ Pending | After implementation |

---

## Completed Tasks (Setup Phase)

### ✅ Task Group 1: Project Setup
- [x] Create GitHub repository structure
- [x] Initialize with README.md and .gitignore
- [x] Set up `/specs/phase1/` folder structure
- [x] Create root `CLAUDE.md` with project guidelines
- [x] Create `constitution.md` with project principles
- [x] Configure `pyproject.toml` for UV
- [x] Set up virtual environment with UV
- [x] Create all Phase I specifications:
  - [x] `requirements.md`
  - [x] `data-model.md`
  - [x] `ui-spec.md`
  - [x] `acceptance-criteria.md`
  - [x] `features/add-task.md`
  - [x] `features/view-tasks.md`
  - [x] `features/update-task.md`
  - [x] `features/delete-task.md`
  - [x] `features/mark-complete.md`
- [x] Create `CLARIFICATIONS.md`
- [x] Create `DEVELOPMENT-PLAN.md`

---

## Pending Tasks (Implementation Phase)

### ⬜ Task Group 2: Core Implementation

#### Task 2.1: Data Model (`src/todo/models.py`)
**Spec Source**: `specs/phase1/data-model.md`

- [ ] Create `Task` dataclass with fields:
  - [ ] `id: int`
  - [ ] `title: str`
  - [ ] `description: str`
  - [ ] `completed: bool`
  - [ ] `created_at: datetime`
  - [ ] `updated_at: datetime | None`
- [ ] Implement `validate_title(title: str) -> tuple[bool, str]`
- [ ] Implement `validate_description(desc: str) -> tuple[bool, str]`
- [ ] Implement `validate_id(id_input: str, existing_ids: set) -> tuple[bool, int | str]`

**Validation Rules**:
- Title: 1-200 chars, non-empty after strip
- Description: 0-1000 chars
- ID: positive integer, must exist

---

#### Task 2.2: Task Manager (`src/todo/manager.py`)
**Spec Source**: `specs/phase1/data-model.md` Section 3

- [ ] Create `TaskManager` class with:
  - [ ] `_tasks: dict[int, Task]`
  - [ ] `_next_id: int`
- [ ] Implement methods:
  - [ ] `add(title, description="") -> Task`
  - [ ] `get_all() -> list[Task]`
  - [ ] `get(id) -> Task | None`
  - [ ] `update(id, title?, description?) -> bool`
  - [ ] `delete(id) -> bool`
  - [ ] `toggle_complete(id) -> bool`
  - [ ] `get_stats() -> dict` (total, completed, pending)

**Key Behaviors**:
- IDs auto-increment starting from 1
- Deleted IDs are NOT reused
- `update` sets `updated_at` timestamp
- `toggle_complete` sets `updated_at` timestamp

---

#### Task 2.3: User Interface (`src/todo/ui.py`)
**Spec Source**: `specs/phase1/ui-spec.md`

- [ ] Create display constants:
  - [ ] Box drawing characters
  - [ ] Status indicators (`[ ]`, `[x]`)
  - [ ] Message icons (`✓`, `✗`, `ℹ`, `⚠`)
- [ ] Implement functions:
  - [ ] `show_menu() -> None`
  - [ ] `show_success(message: str) -> None`
  - [ ] `show_error(message: str) -> None`
  - [ ] `show_info(message: str) -> None`
  - [ ] `format_task(task: Task) -> str`
  - [ ] `format_task_list(tasks: list[Task]) -> str`
  - [ ] `get_input(prompt: str) -> str`
  - [ ] `get_validated_input(prompt, validator) -> str`
  - [ ] `confirm(prompt: str, default: bool = False) -> bool`

---

#### Task 2.4: Main Application (`src/todo/__main__.py`)
**Spec Source**: `specs/phase1/features/*.md`

- [ ] Import models, manager, ui modules
- [ ] Create `TodoApp` class with:
  - [ ] `manager: TaskManager`
  - [ ] `running: bool`
- [ ] Implement feature methods:
  - [ ] `add_task() -> None`
  - [ ] `view_tasks() -> None`
  - [ ] `update_task() -> None`
  - [ ] `delete_task() -> None`
  - [ ] `mark_complete() -> None`
- [ ] Implement main loop:
  - [ ] `run() -> None`
  - [ ] `handle_menu_choice(choice: str) -> None`
- [ ] Implement graceful exit:
  - [ ] Handle `KeyboardInterrupt`
  - [ ] Handle menu option 0
- [ ] Create `main()` entry point

---

### ⬜ Task Group 3: Testing

#### Task 3.1: Model Tests (`tests/test_models.py`)
- [ ] Test `Task` creation with defaults
- [ ] Test `Task` creation with all fields
- [ ] Test `validate_title`:
  - [ ] Empty string → error
  - [ ] Whitespace only → error
  - [ ] Valid title → success
  - [ ] 200 chars → success
  - [ ] 201 chars → error
- [ ] Test `validate_description`:
  - [ ] Empty string → success
  - [ ] 1000 chars → success
  - [ ] 1001 chars → error
- [ ] Test `validate_id`:
  - [ ] Non-numeric → error
  - [ ] Negative → error
  - [ ] Not found → error
  - [ ] Valid → success

---

#### Task 3.2: Manager Tests (`tests/test_manager.py`)
- [ ] Test `add` creates task with correct ID
- [ ] Test `add` increments ID
- [ ] Test `get_all` returns all tasks
- [ ] Test `get_all` returns empty list
- [ ] Test `get` returns correct task
- [ ] Test `get` returns None for missing
- [ ] Test `update` modifies fields
- [ ] Test `update` sets updated_at
- [ ] Test `update` returns False for missing
- [ ] Test `delete` removes task
- [ ] Test `delete` doesn't reuse ID
- [ ] Test `toggle_complete` toggles status
- [ ] Test `toggle_complete` sets updated_at

---

#### Task 3.3: Integration Tests (`tests/test_integration.py`)
- [ ] Test full add → view workflow
- [ ] Test add → update → view workflow
- [ ] Test add → delete → view workflow
- [ ] Test add → toggle → view workflow
- [ ] Test multiple operations maintain integrity

---

### ⬜ Task Group 4: Validation

#### Task 4.1: Acceptance Criteria Validation
**Source**: `specs/phase1/acceptance-criteria.md`

Run manual tests for each criterion:

**Startup (AC-1.x)**:
- [ ] AC-1.1: Clean start with `uv run python -m todo`
- [ ] AC-1.2: Menu displays all 6 options

**Add Task (AC-2.x)**:
- [ ] AC-2.1: Add with title only
- [ ] AC-2.2: Add with title and description
- [ ] AC-2.3: Empty title validation
- [ ] AC-2.4: Title length validation
- [ ] AC-2.5: Description length validation

**View Tasks (AC-3.x)**:
- [ ] AC-3.1: Empty list message
- [ ] AC-3.2: Display all tasks
- [ ] AC-3.3: Status indicators correct
- [ ] AC-3.4: Description truncation

**Update Task (AC-4.x)**:
- [ ] AC-4.1: Update title only
- [ ] AC-4.2: Update description only
- [ ] AC-4.3: Update both fields
- [ ] AC-4.4: No changes made
- [ ] AC-4.5: Invalid task ID
- [ ] AC-4.6: No tasks to update

**Delete Task (AC-5.x)**:
- [ ] AC-5.1: Delete with confirmation
- [ ] AC-5.2: Cancel deletion
- [ ] AC-5.3: Default to cancel
- [ ] AC-5.4: Invalid task ID
- [ ] AC-5.5: No tasks to delete

**Mark Complete (AC-6.x)**:
- [ ] AC-6.1: Mark pending as complete
- [ ] AC-6.2: Mark complete as pending
- [ ] AC-6.3: Toggle updates timestamp
- [ ] AC-6.4: Invalid task ID

**Exit (AC-7.x)**:
- [ ] AC-7.1: Clean exit via menu
- [ ] AC-7.2: Clean exit via Ctrl+C

**Error Handling (AC-8.x)**:
- [ ] AC-8.1: Invalid menu choice
- [ ] AC-8.2: Non-numeric ID input

**Data Integrity (AC-9.x)**:
- [ ] AC-9.1: Unique IDs
- [ ] AC-9.2: ID not reused
- [ ] AC-9.3: Data preserved in memory

---

#### Task 4.2: Code Quality Checks
- [ ] Run `uv run ruff check src/`
- [ ] Run `uv run ruff format src/ --check`
- [ ] Verify type hints on all functions
- [ ] Verify docstrings on public methods
- [ ] No external dependencies used

---

### ⬜ Task Group 5: Submission

#### Task 5.1: Documentation Review
- [ ] README.md has all required sections
- [ ] Commands in README work correctly
- [ ] CLAUDE.md is up to date
- [ ] Feature checklist updated

#### Task 5.2: Demo Video (90 seconds)
Script:
```
00:00-00:10  Show GitHub repo, project structure
00:10-00:20  Run: uv run python -m todo
00:20-00:35  Demo: Add two tasks
00:35-00:45  Demo: View tasks
00:45-00:55  Demo: Update a task
00:55-01:05  Demo: Mark task complete
01:05-01:15  Demo: Delete a task (with confirmation)
01:15-01:25  Demo: Error handling (invalid input)
01:25-01:30  Exit, show goodbye message
```

- [ ] Record video
- [ ] Verify under 90 seconds
- [ ] Upload to accessible location

#### Task 5.3: Final Submission
- [ ] GitHub repository is public
- [ ] All files committed
- [ ] Submit by deadline

---

## Not In Scope for Phase I

These items from the task breakdown are deferred to later phases:

| Task | Deferred To |
|------|-------------|
| `.spec-kit/config.yaml` | Not needed for Phase I |
| `/specs/api/` folder | Phase II |
| `/specs/database/` folder | Phase II |
| Color coding | Phase II (rich library) |
| Task categorization | Phase II |
| Due dates | Phase II |
| Export (CSV/JSON) | Phase II |
| Logging | Phase II |

---

## Quick Reference: Implementation Order

```
1. models.py     ← Start here (no dependencies)
2. manager.py    ← Depends on models.py
3. ui.py         ← Depends on models.py
4. __main__.py   ← Depends on all above
5. tests/*.py    ← Test each component
6. Validation    ← Run acceptance criteria
7. Demo          ← Record video
```

---

## Current Action

**Next Step**: Implement `src/todo/models.py`

```bash
# After implementation, verify with:
uv run python -c "from todo.models import Task; print(Task)"
```
