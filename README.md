
# Todo App Evolution - Hackathon II

A spec-driven development project transforming a simple console app into a cloud-native AI-powered system.

## Current Phase: Phase I - Console App

In-memory Python todo application with 5 core features.

## Quick Start

### Prerequisites
- Python 3.13+
- [UV package manager](https://docs.astral.sh/uv/)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/todo-app.git
cd todo-app

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync
```

### Run the Application

```bash
uv run python -m todo
```

### Run Tests

```bash
uv run pytest
```

## Features

| Feature | Description | Status |
|---------|-------------|--------|
| Add Task | Create new tasks with title and description | ✅ |
| View Tasks | Display all tasks with status | ✅ |
| Update Task | Modify existing task details | ✅ |
| Delete Task | Remove tasks with confirmation | ✅ |
| Mark Complete | Toggle task completion status | ✅ |

## Project Structure

```
todo-app/
├── specs/                  # Specifications (read first!)
│   └── phase1/
│       ├── requirements.md
│       ├── data-model.md
│       ├── ui-spec.md
│       ├── acceptance-criteria.md
│       └── features/
├── src/todo/               # Application source code
│   ├── __init__.py
│   ├── __main__.py
│   ├── models.py
│   ├── manager.py
│   └── ui.py
├── tests/                  # Test files
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── CLAUDE.md               # Claude Code instructions
└── constitution.md         # Project principles
```

## Development Approach

This project uses **spec-driven development**:

1. **Write specifications** - Define features in markdown
2. **Generate code** - Use Claude Code to implement specs
3. **Validate** - Test against acceptance criteria
4. **Refine** - Iterate on specs until correct

See [CLAUDE.md](CLAUDE.md) for detailed development instructions.

## Usage Example

```
╔══════════════════════════════════════╗
║         TODO APP - Phase I           ║
╠══════════════════════════════════════╣
║                                      ║
║   1. Add Task                        ║
║   2. View Tasks                      ║
║   3. Update Task                     ║
║   4. Delete Task                     ║
║   5. Mark Complete                   ║
║   0. Exit                            ║
║                                      ║
╚══════════════════════════════════════╝

Enter your choice: 1

=== Add New Task ===

Enter task title: Buy groceries
Enter description (optional): Get milk, eggs, and bread

✓ Task added successfully!
  ID: #1
  Title: Buy groceries
```

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| I | Console App (In-Memory) | ✅ Complete |
| II | Web App (Flask/React) | ⬜ Planned |
| III | AI Chatbot (MCP Tools) | ⬜ Planned |
| IV | Kubernetes Deployment | ⬜ Planned |
| V | Cloud-Native Architecture | ⬜ Planned |

## License

MIT License - See LICENSE file for details.

## Contributing

This is a hackathon project demonstrating spec-driven development with AI. Contributions should follow the spec-first approach documented in [CLAUDE.md](CLAUDE.md).

