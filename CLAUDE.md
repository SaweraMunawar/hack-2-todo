# Claude Code Instructions

## Project Overview
This is the "Evolution of Todo" hackathon project - a spec-driven development exercise building a todo application that evolves from console to cloud-native.

**Current Phase**: Phase I - Todo In-Memory Python Console App

## Spec-Driven Development Rules

### MUST Follow
1. **Read specifications first** - All specs are in `/specs/phase1/`
2. **Generate code from specs** - Do not write code manually
3. **Use UV package manager** - All Python commands use `uv run`
4. **Validate against acceptance criteria** - See `specs/phase1/acceptance-criteria.md`

### MUST NOT Do
- Write code without reading the relevant specification
- Use pip directly (use UV instead)
- Add features not in specifications
- Skip validation steps

## Project Structure

```
todo-app/
├── specs/phase1/           # Specifications (READ FIRST)
│   ├── requirements.md     # High-level requirements
│   ├── data-model.md       # Task data structure
│   ├── ui-spec.md          # UI formatting rules
│   ├── acceptance-criteria.md
│   └── features/           # Individual feature specs
│       ├── add-task.md
│       ├── view-tasks.md
│       ├── update-task.md
│       ├── delete-task.md
│       └── mark-complete.md
├── src/todo/               # Source code
│   ├── __init__.py
│   ├── __main__.py         # Entry point
│   ├── models.py           # Task dataclass
│   ├── manager.py          # TaskManager class
│   └── ui.py               # User interface
├── tests/                  # Test files
├── pyproject.toml          # UV project config
├── README.md               # Setup instructions
├── CLAUDE.md               # This file
└── constitution.md         # Project principles
```

## Key Commands

```bash
# Run the application
uv run python -m todo

# Run tests
uv run pytest

# Format code
uv run ruff format src/

# Lint code
uv run ruff check src/
```

## Implementation Workflow

### 1. Read Specifications
```bash
# Start with requirements
cat specs/phase1/requirements.md

# Then data model
cat specs/phase1/data-model.md

# Then individual features
cat specs/phase1/features/*.md
```

### 2. Generate Code
- Implement models.py from data-model.md
- Implement manager.py for TaskManager
- Implement ui.py from ui-spec.md
- Implement __main__.py for entry point

### 3. Validate
- Run the application: `uv run python -m todo`
- Test each acceptance criterion
- Fix issues by refining specs, then regenerating

## Feature Checklist

| Feature | Spec File | Status |
|---------|-----------|--------|
| Add Task | features/add-task.md | ✅ |
| View Tasks | features/view-tasks.md | ✅ |
| Update Task | features/update-task.md | ✅ |
| Delete Task | features/delete-task.md | ✅ |
| Mark Complete | features/mark-complete.md | ✅ |

## Code Quality Requirements

- Python 3.13+ features allowed
- Type hints on all functions
- Docstrings for public methods
- PEP 8 compliant (use ruff)
- No external dependencies beyond standard library

## Error Handling

- Never show stack traces to users
- Catch KeyboardInterrupt gracefully
- Validate all user input
- Provide helpful error messages

## Testing Notes

- Test with empty task list
- Test with multiple tasks
- Test invalid inputs
- Test edge cases (max length strings)
- Test Ctrl+C handling
