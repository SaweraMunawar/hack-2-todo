# Phase I Clarifications Document

## Document Information
- **Version**: 1.0.0
- **Last Updated**: 2024-01-XX

---

## 1. Spec-Kit Plus Implementation

### Q: What specific conventions should we follow for specification files?

**A: Spec-Kit Plus Convention (Simplified for Phase I)**

Each specification file should follow this structure:
```markdown
# [Feature/Component] Specification

## Document Information
- Phase: I
- Version: 1.0.0

## Overview
Brief description of what this spec covers.

## Requirements
Detailed requirements with clear acceptance criteria.

## Implementation Notes
Technical guidance for code generation.
```

### Q: How should we structure the `/specs` folder?

**A: Current Structure (Already Implemented)**
```
specs/
└── phase1/
    ├── README.md              # Overview and navigation
    ├── requirements.md        # High-level requirements
    ├── data-model.md          # Data structures
    ├── ui-spec.md             # UI formatting
    ├── acceptance-criteria.md # Test scenarios
    └── features/              # One file per feature
        ├── add-task.md
        ├── view-tasks.md
        ├── update-task.md
        ├── delete-task.md
        └── mark-complete.md
```

**Note**: No `.spec-kit` folder is required for Phase I. The simplified approach uses the `/specs` directory directly.

### Q: Are there template specification files?

**A: Yes, use this template for feature specs:**

```markdown
# Feature Specification: [Feature Name]

## Feature ID: F[N]

## Overview
[One sentence description]

## User Story
**As a** user
**I want to** [action]
**So that** [benefit]

## Functional Requirements
### Inputs
| Field | Required | Validation |
|-------|----------|------------|

### Process Flow
1. Step one
2. Step two
...

### Outputs
- Success case
- Error cases

## User Interface
[Prompts and messages]

## Edge Cases
| Scenario | Expected Behavior |
|----------|-------------------|

## Implementation Notes
[Technical details]
```

---

## 2. Claude Code Integration

### Q: What is the expected workflow between writing specs and using Claude Code?

**A: Three-Step Workflow**

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   1. SPECIFY    │ ──▶ │   2. GENERATE   │ ──▶ │   3. VALIDATE   │
│ Write/refine    │     │ Claude Code     │     │ Test against    │
│ specs in /specs │     │ generates code  │     │ acceptance      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                                              │
         │                                              │
         └──────────── Refine if needed ───────────────┘
```

**Detailed Steps:**
1. **SPECIFY**: Write detailed specs with examples and edge cases
2. **GENERATE**: Tell Claude Code "Implement [feature] from specs/phase1/features/[feature].md"
3. **VALIDATE**: Run the app, test acceptance criteria
4. **ITERATE**: If issues, refine spec (not code), then regenerate

### Q: How should we organize CLAUDE.md files?

**A: Single Root-Level File for Phase I**

For Phase I (monolithic console app), use ONE `CLAUDE.md` at the project root.

```
todo-app/
├── CLAUDE.md          # ← Single file for Phase I
├── constitution.md
└── ...
```

For later phases with frontend/backend separation:
```
todo-app/
├── CLAUDE.md          # Root-level overview
├── frontend/
│   └── CLAUDE.md      # Frontend-specific instructions
└── backend/
    └── CLAUDE.md      # Backend-specific instructions
```

### Q: What prompts work best with Claude Code?

**A: Recommended Prompt Patterns**

```
# For implementation
"Read specs/phase1/data-model.md and implement src/todo/models.py"

# For feature implementation
"Implement the Add Task feature according to specs/phase1/features/add-task.md"

# For validation
"Test the application against specs/phase1/acceptance-criteria.md"

# For fixes
"The [feature] doesn't match the spec. The spec says [X] but implementation does [Y]. Fix to match spec."
```

---

## 3. Phase I Specific Questions

### Q: What data structure should in-memory storage use?

**A: Dictionary with Dataclass**

```python
# models.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime | None

# manager.py
class TaskManager:
    _tasks: dict[int, Task]  # ID → Task mapping
    _next_id: int            # Auto-increment counter
```

**Rationale:**
- `dict[int, Task]`: O(1) lookup by ID
- `dataclass`: Clean, type-safe, minimal boilerplate
- Separate `TaskManager` class for operations

### Q: What error handling depth is required?

**A: Comprehensive Input Validation**

| Category | Required Handling |
|----------|-------------------|
| Empty input | Show error, re-prompt |
| Invalid type | Show error, re-prompt |
| Out of range | Show error, re-prompt |
| ID not found | Show error, re-prompt |
| Keyboard interrupt | Exit gracefully |
| Unexpected errors | Catch-all with friendly message |

**Error Message Format:**
```
✗ Error: [Specific problem description]
```

### Q: Which Python libraries to use or avoid?

**A: Standard Library Only**

**USE:**
- `dataclasses` - Data models
- `datetime` - Timestamps
- `typing` - Type hints

**AVOID:**
- `rich`, `textual` - Too complex for Phase I
- `click`, `typer` - Overkill for simple menu
- Any external dependencies

**Why:** Phase I demonstrates core Python skills without dependency management complexity.

---

## 4. Project Structure Details

### Q: What files should be in `.spec-kit` folder?

**A: NOT REQUIRED for Phase I**

The `.spec-kit` folder is optional for complex multi-phase projects. For Phase I, use the simplified structure:

```
specs/phase1/    # All specs here
CLAUDE.md        # Instructions at root
constitution.md  # Principles at root
```

### Q: How to configure `config.yaml`?

**A: NOT REQUIRED for Phase I**

No config.yaml needed. The project structure is simple enough that:
- `pyproject.toml` handles Python configuration
- `CLAUDE.md` provides Claude Code instructions
- Specs are self-contained in `/specs/phase1/`

### Q: What should CLAUDE.md include?

**A: Already Created - Key Sections:**

1. Project Overview
2. Current Phase
3. Spec-Driven Rules (MUST/MUST NOT)
4. Project Structure
5. Key Commands
6. Implementation Workflow
7. Feature Checklist
8. Code Quality Requirements
9. Error Handling Guidelines

---

## 5. Development Environment

### Q: WSL 2 specific instructions?

**A: Minimal Additional Setup**

```bash
# Ensure Python 3.13+ is available
python3 --version

# Install UV (if not already)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to project (use /mnt/d/ for Windows drives)
cd /mnt/d/Hack-todo

# Sync project
uv sync

# Run application
uv run python -m todo
```

**WSL Notes:**
- Use `/mnt/c/` or `/mnt/d/` to access Windows drives
- VS Code with WSL extension works seamlessly
- Git should be configured in WSL, not Windows

### Q: Virtual environment handling?

**A: UV Only (No venv/conda)**

```bash
# UV creates .venv automatically
uv sync          # Creates .venv and installs deps

# All commands use uv run
uv run python -m todo
uv run pytest
uv run ruff check src/
```

**Why UV:**
- Single tool for Python version + deps + venv
- Faster than pip/poetry
- Modern, hackathon-aligned choice

### Q: Testing framework for Phase I?

**A: pytest**

```bash
# Install (already in dev dependencies)
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/todo
```

**Test structure:**
```
tests/
├── __init__.py
├── test_models.py
├── test_manager.py
└── test_ui.py
```

---

## 6. Submission Requirements

### Q: What must be in the demo video?

**A: 90-Second Demo Checklist**

| Time | Content |
|------|---------|
| 0:00-0:10 | Project intro, show GitHub repo |
| 0:10-0:20 | Run `uv run python -m todo` |
| 0:20-0:35 | Demo: Add Task |
| 0:35-0:45 | Demo: View Tasks |
| 0:45-0:55 | Demo: Update Task |
| 0:55-1:05 | Demo: Delete Task (with confirmation) |
| 1:05-1:15 | Demo: Mark Complete (toggle) |
| 1:15-1:25 | Show error handling (invalid input) |
| 1:25-1:30 | Exit cleanly, brief summary |

### Q: How detailed should README.md be?

**A: Practical and Concise**

Required sections:
1. **Project Title** - One line
2. **Quick Start** - 5 commands max
3. **Features** - Bullet list
4. **Project Structure** - Directory tree
5. **Usage Example** - Screenshot or code block
6. **Development** - How to run tests/lint

### Q: What is "comprehensive documentation"?

**A: For Phase I:**

- [x] README.md - Setup and usage
- [x] CLAUDE.md - Development workflow
- [x] constitution.md - Project principles
- [x] specs/phase1/*.md - All feature specs
- [x] Docstrings in code
- [ ] Demo video (90 seconds)

---

## 7. Data Persistence

### Q: Should tasks persist across restarts?

**A: NO - In-Memory Only**

Phase I explicitly uses **in-memory storage**:
- Tasks exist only while the application runs
- Closing the app loses all data
- This is intentional and acceptable

**Rationale:**
- Phase I focuses on core CRUD logic
- Persistence is added in Phase II (SQLite)
- Keeps Phase I simple and focused

---

## 8. User Interface

### Q: Simple text-based or use rich/textual?

**A: Simple Text-Based with Unicode**

```python
# Use basic Unicode for visual appeal
ICONS = {
    "success": "✓",
    "error": "✗",
    "pending": "[ ]",
    "complete": "[x]",
}

# Box drawing for menu
╔══════════════════════════════════════╗
║         TODO APP - Phase I           ║
╚══════════════════════════════════════╝
```

**NO external libraries** - Use only:
- `print()` for output
- `input()` for prompts
- Unicode characters for decoration

### Q: What polish level is expected?

**A: Functional and Clean**

| Aspect | Expectation |
|--------|-------------|
| Menu | Clear, numbered options |
| Prompts | Descriptive, consistent |
| Output | Formatted, readable |
| Errors | Helpful, not scary |
| Flow | Predictable, logical |

---

## 9. Error Handling

### Q: How comprehensive?

**A: All User-Facing Inputs**

```python
# Required validation
- Empty string → "Title cannot be empty"
- Too long → "Title must be 200 characters or less"
- Non-numeric ID → "Please enter a valid number"
- ID not found → "Task with ID X not found"
- Ctrl+C → Clean exit, no stack trace
```

### Q: Validate all inputs?

**A: Yes, with Helpful Messages**

```python
def get_validated_input(prompt: str, validator: Callable) -> str:
    """Get input with validation and error messages."""
    while True:
        value = input(prompt).strip()
        is_valid, result = validator(value)
        if is_valid:
            return result
        print(f"✗ Error: {result}")
```

---

## 10. Feature Scope

### Q: Only Basic Level for Phase I?

**A: YES - Only 5 Basic Features**

| Feature | Phase I | Later Phases |
|---------|---------|--------------|
| Add Task | ✅ | - |
| View Tasks | ✅ | - |
| Update Task | ✅ | - |
| Delete Task | ✅ | - |
| Mark Complete | ✅ | - |
| Priorities | ❌ | Phase II |
| Due Dates | ❌ | Phase II |
| Categories | ❌ | Phase II |
| Persistence | ❌ | Phase II |
| AI Chatbot | ❌ | Phase III |

### Q: Any "nice-to-have" features?

**A: NO - Stick to Spec**

The constitution says: "MUST implement all Basic, Intermediate, and Advanced level features **progressively**"

- Phase I = Basic only
- Adding extra features violates spec-driven principles
- Save enhancements for Phase II

---

## 11. Code Quality Standards

### Q: Which style guide?

**A: PEP 8 with Ruff**

```bash
# Format code
uv run ruff format src/

# Check for issues
uv run ruff check src/

# Fix auto-fixable issues
uv run ruff check src/ --fix
```

### Q: Required linters/formatters?

**A: Ruff Only**

Already configured in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "W"]
```

### Q: Testing coverage expectation?

**A: Core Logic Coverage**

Minimum:
- `test_models.py` - Task creation, validation
- `test_manager.py` - All CRUD operations
- Basic happy path + key edge cases

Nice to have:
- 80%+ coverage
- Edge case coverage
- Integration tests

---

## 12. UV Integration

### Q: pyproject.toml or requirements.txt?

**A: pyproject.toml Only**

```toml
[project]
name = "todo"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.4"]
```

**No requirements.txt** - UV uses pyproject.toml exclusively.

### Q: Dependency management?

**A: UV Commands**

```bash
# Initial setup
uv sync

# Add dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Remove dependency
uv remove package-name
```

---

## 13. Git Practices

### Q: Branching strategy?

**A: Simple for Phase I**

```
main
 └── feature/[feature-name]  (optional for larger changes)
```

**Commit message format:**
```
type: brief description

- Detail 1
- Detail 2
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`

### Q: .gitignore template?

**A: Already Created**

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/

# UV
.python-version

# IDE
.vscode/
.idea/

# Testing
.pytest_cache/
.coverage

# Build
dist/
*.egg-info/
```

---

## Summary: Phase I Checklist

| Requirement | Status |
|-------------|--------|
| Specs in `/specs/phase1/` | ✅ |
| CLAUDE.md | ✅ |
| constitution.md | ✅ |
| README.md | ✅ |
| pyproject.toml (UV) | ✅ |
| .gitignore | ✅ |
| 5 Basic Features | ⬜ Pending |
| pytest tests | ⬜ Pending |
| Demo video | ⬜ Pending |
