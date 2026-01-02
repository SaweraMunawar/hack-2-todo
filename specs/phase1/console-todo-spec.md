# Phase 1: Console Todo Application Specification

## Overview
A command-line todo application built in Python that demonstrates progressive feature evolution from basic CRUD to advanced functionality.

## Technology Stack
- **Language**: Python 3.10+
- **Storage**: JSON file persistence
- **Interface**: Interactive command-line menu

---

## Feature Levels

### Basic Level
Core CRUD operations for todo management.

#### Features
1. **Add Todo**: Create a new todo item with a title
2. **List Todos**: Display all todos with their status
3. **Complete Todo**: Mark a todo as completed
4. **Delete Todo**: Remove a todo from the list

#### Data Model (Basic)
```python
{
    "id": int,          # Unique identifier
    "title": str,       # Todo description
    "completed": bool,  # Completion status
    "created_at": str   # ISO timestamp
}
```

---

### Intermediate Level
Enhanced todo items with additional metadata.

#### Features
1. **Priority Levels**: Set priority (low, medium, high, critical)
2. **Due Dates**: Assign optional due dates to todos
3. **Categories/Tags**: Organize todos with categories
4. **Filter by Status**: View only pending or completed todos
5. **Filter by Priority**: View todos by priority level

#### Data Model (Intermediate)
```python
{
    "id": int,
    "title": str,
    "completed": bool,
    "created_at": str,
    "priority": str,      # "low" | "medium" | "high" | "critical"
    "due_date": str | None,  # ISO date or null
    "category": str       # User-defined category
}
```

---

### Advanced Level
Production-ready features for power users.

#### Features
1. **JSON File Persistence**: Save/load todos from disk
2. **Search**: Find todos by keyword in title
3. **Statistics**: Show completion rates, overdue counts
4. **Sort Options**: Sort by date, priority, or status
5. **Edit Todo**: Modify existing todo properties
6. **Bulk Operations**: Complete/delete multiple todos

#### Data Model (Advanced)
```python
{
    "id": int,
    "title": str,
    "completed": bool,
    "created_at": str,
    "updated_at": str,    # Last modification timestamp
    "completed_at": str | None,  # When marked complete
    "priority": str,
    "due_date": str | None,
    "category": str,
    "tags": list[str]     # Multiple tags support
}
```

---

## User Interface

### Main Menu
```
╔════════════════════════════════════╗
║     TODO APP - Phase 1 Console     ║
╠════════════════════════════════════╣
║  1. Add Todo                       ║
║  2. List Todos                     ║
║  3. Complete Todo                  ║
║  4. Delete Todo                    ║
║  5. Edit Todo                      ║
║  6. Search Todos                   ║
║  7. Filter Todos                   ║
║  8. Sort Todos                     ║
║  9. Statistics                     ║
║  0. Exit                           ║
╚════════════════════════════════════╝
```

### Display Format
```
[1] ☐ Buy groceries          [HIGH]  Due: 2024-01-15  #shopping
[2] ☑ Call mom               [LOW]   Done: 2024-01-10  #personal
[3] ☐ Finish report          [CRIT]  Due: 2024-01-12  #work
```

---

## File Structure
```
src/
├── __init__.py
├── main.py           # Entry point, main menu loop
├── todo.py           # Todo class and data model
├── storage.py        # JSON persistence layer
├── display.py        # Console UI formatting
└── utils.py          # Helper functions (dates, validation)

tests/
├── __init__.py
├── test_todo.py
├── test_storage.py
└── test_utils.py

data/
└── todos.json        # Persisted todos (created at runtime)
```

---

## Implementation Notes

### Error Handling
- Validate all user inputs
- Handle file I/O errors gracefully
- Provide clear error messages

### User Experience
- Auto-save after each operation
- Confirm destructive actions
- Support keyboard interrupt (Ctrl+C) gracefully

### Code Quality
- Type hints on all functions
- Docstrings for public methods
- PEP 8 compliant
