# Development Plan: Phase I Implementation

## Document Information
- **Phase**: I - Todo In-Memory Python Console App
- **Target Completion**: Current Sprint
- **Status**: Ready for Implementation

---

## Executive Summary

Phase I specifications are **complete**. This document provides the implementation roadmap to generate working code from specifications using Claude Code.

### Current State
| Component | Status |
|-----------|--------|
| Specifications | ✅ Complete (11 files) |
| Project Structure | ✅ Set up |
| UV Environment | ✅ Configured |
| Source Code | ⬜ Skeleton only |
| Tests | ⬜ Not started |
| Demo Video | ⬜ Not started |

---

## Implementation Roadmap

### Step 1: Data Model Implementation
**Source Spec**: `specs/phase1/data-model.md`
**Target File**: `src/todo/models.py`

```
Tasks:
1. Read data-model.md specification
2. Generate Task dataclass with all fields
3. Generate validation functions
4. Verify field constraints match spec
```

**Acceptance Criteria**:
- [ ] Task dataclass with: id, title, description, completed, created_at, updated_at
- [ ] validate_title() returns (bool, str)
- [ ] validate_description() returns (bool, str)
- [ ] validate_id() returns (bool, int|str)

---

### Step 2: Task Manager Implementation
**Source Spec**: `specs/phase1/data-model.md` (Section 3)
**Target File**: `src/todo/manager.py`

```
Tasks:
1. Generate TaskManager class
2. Implement CRUD operations
3. Ensure ID auto-increment
4. Verify ID not reused after deletion
```

**Acceptance Criteria**:
- [ ] add(title, description) → Task
- [ ] get_all() → list[Task]
- [ ] get(id) → Task | None
- [ ] update(id, title?, description?) → bool
- [ ] delete(id) → bool
- [ ] toggle_complete(id) → bool

---

### Step 3: User Interface Implementation
**Source Spec**: `specs/phase1/ui-spec.md`
**Target File**: `src/todo/ui.py`

```
Tasks:
1. Generate menu display with box drawing
2. Implement message formatting (success/error/info)
3. Create task display formatters
4. Handle input prompts
```

**Acceptance Criteria**:
- [ ] Main menu with box drawing characters
- [ ] Success messages with ✓ prefix
- [ ] Error messages with ✗ prefix
- [ ] Task list formatting with status indicators

---

### Step 4: Feature Implementation
**Source Specs**: `specs/phase1/features/*.md`
**Target File**: `src/todo/__main__.py`

```
Implementation Order:
1. Add Task (F1) - specs/phase1/features/add-task.md
2. View Tasks (F2) - specs/phase1/features/view-tasks.md
3. Mark Complete (F5) - specs/phase1/features/mark-complete.md
4. Update Task (F3) - specs/phase1/features/update-task.md
5. Delete Task (F4) - specs/phase1/features/delete-task.md
```

**Why This Order**:
- Add → View: Need tasks to view
- View → Mark: Need to see status changes
- Mark → Update: Similar ID selection pattern
- Update → Delete: Delete needs confirmation pattern

**Acceptance Criteria per Feature**:

#### F1: Add Task
- [ ] Prompt for title (required)
- [ ] Prompt for description (optional)
- [ ] Validate inputs per spec
- [ ] Display success message with ID

#### F2: View Tasks
- [ ] Handle empty list
- [ ] Display all tasks with formatting
- [ ] Show status indicators [ ] and [x]
- [ ] Truncate long descriptions
- [ ] Show summary counts

#### F5: Mark Complete
- [ ] Show current tasks with status
- [ ] Prompt for ID
- [ ] Toggle status
- [ ] Show confirmation message

#### F3: Update Task
- [ ] Check for empty task list
- [ ] Show current tasks
- [ ] Prompt for ID
- [ ] Allow keeping current values
- [ ] Validate new inputs
- [ ] Track updated_at

#### F4: Delete Task
- [ ] Check for empty task list
- [ ] Show current tasks
- [ ] Prompt for ID
- [ ] Require confirmation (default=No)
- [ ] Show appropriate message

---

### Step 5: Main Application Loop
**Source Spec**: `specs/phase1/ui-spec.md`
**Target File**: `src/todo/__main__.py`

```
Tasks:
1. Create main menu loop
2. Route menu choices to features
3. Handle invalid choices
4. Implement clean exit (menu and Ctrl+C)
```

**Acceptance Criteria**:
- [ ] Menu displays on start
- [ ] All 6 options work (1-5 + 0)
- [ ] Invalid input shows error, re-prompts
- [ ] Ctrl+C exits gracefully
- [ ] Option 0 exits with goodbye message

---

### Step 6: Testing
**Source Spec**: `specs/phase1/acceptance-criteria.md`
**Target Files**: `tests/test_*.py`

```
Test Files:
1. tests/test_models.py - Task and validation
2. tests/test_manager.py - CRUD operations
3. tests/test_integration.py - End-to-end scenarios
```

**Key Test Scenarios** (from acceptance-criteria.md):
- [ ] AC-1.x: Application startup
- [ ] AC-2.x: Add Task (5 criteria)
- [ ] AC-3.x: View Tasks (4 criteria)
- [ ] AC-4.x: Update Task (6 criteria)
- [ ] AC-5.x: Delete Task (5 criteria)
- [ ] AC-6.x: Mark Complete (4 criteria)
- [ ] AC-7.x: Exit (2 criteria)
- [ ] AC-8.x: Error handling (2 criteria)
- [ ] AC-9.x: Data integrity (3 criteria)

---

### Step 7: Documentation & Demo
**Target**: README.md + 90-second video

```
Documentation Tasks:
1. Verify README.md has all required sections
2. Test all commands in README work
3. Prepare demo script

Demo Video Script (90 seconds):
00:00-00:10  Show GitHub repo, project structure
00:10-00:20  Run: uv run python -m todo
00:20-00:35  Demo: Add two tasks
00:35-00:45  Demo: View tasks
00:45-00:55  Demo: Update a task
00:55-01:05  Demo: Mark task complete
01:05-01:15  Demo: Delete a task (show confirmation)
01:15-01:25  Demo: Error handling (invalid input)
01:25-01:30  Exit, show goodbye message
```

---

## Implementation Commands

### Generate Each Component

```bash
# Step 1: Models
# Prompt: "Read specs/phase1/data-model.md and implement src/todo/models.py"

# Step 2: Manager
# Prompt: "Read specs/phase1/data-model.md section 3 and implement src/todo/manager.py"

# Step 3: UI
# Prompt: "Read specs/phase1/ui-spec.md and implement src/todo/ui.py"

# Step 4-5: Main App
# Prompt: "Read all feature specs in specs/phase1/features/ and implement src/todo/__main__.py"

# Step 6: Tests
# Prompt: "Read specs/phase1/acceptance-criteria.md and create tests in tests/"
```

### Validation Commands

```bash
# Run the application
uv run python -m todo

# Run tests
uv run pytest -v

# Check code quality
uv run ruff check src/
uv run ruff format src/ --check
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Spec ambiguity | Refer to CLARIFICATIONS.md |
| Generation errors | Iterate: refine spec → regenerate |
| Test failures | Check spec compliance first |
| Demo recording | Practice run before recording |

---

## Definition of Done

Phase I is complete when:

1. **Functional**
   - [ ] Application starts: `uv run python -m todo`
   - [ ] All 5 features work per acceptance criteria
   - [ ] No crashes on invalid input
   - [ ] Clean exit via menu and Ctrl+C

2. **Quality**
   - [ ] Code passes ruff checks
   - [ ] Tests pass: `uv run pytest`
   - [ ] Type hints on all functions
   - [ ] Docstrings on public methods

3. **Documentation**
   - [ ] README.md complete
   - [ ] CLAUDE.md complete
   - [ ] constitution.md complete
   - [ ] All specs in /specs

4. **Deliverables**
   - [ ] GitHub repository public
   - [ ] 90-second demo video recorded
   - [ ] Submitted by deadline

---

## Next Action

**Start with Step 1**: Generate `src/todo/models.py` from `specs/phase1/data-model.md`

```
Prompt for Claude Code:
"Read specs/phase1/data-model.md and implement src/todo/models.py with:
- Task dataclass with all specified fields
- validate_title() function
- validate_description() function
- validate_id() function
Follow the exact specifications in the document."
```
