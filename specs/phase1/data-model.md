# Phase I Data Model Specification

## Document Information
- **Phase**: I - Todo In-Memory Python Console App
- **Version**: 1.0.0

---

## 1. Task Entity

### 1.1 Data Structure

```python
@dataclass
class Task:
    id: int                          # Unique identifier
    title: str                       # Task title (required)
    description: str                 # Task description (optional)
    completed: bool                  # Completion status
    created_at: datetime             # Creation timestamp
    updated_at: datetime | None      # Last modification timestamp
```

### 1.2 Field Specifications

| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| `id` | `int` | Yes | Positive integer, auto-generated, unique | Auto-increment |
| `title` | `str` | Yes | 1-200 characters, non-empty after strip | - |
| `description` | `str` | No | 0-1000 characters | `""` (empty string) |
| `completed` | `bool` | Yes | `True` or `False` | `False` |
| `created_at` | `datetime` | Yes | UTC timestamp | Current time on creation |
| `updated_at` | `datetime | None` | No | UTC timestamp or None | `None` (set on update) |

---

## 2. Validation Rules

### 2.1 Title Validation
```python
def validate_title(title: str) -> tuple[bool, str]:
    """
    Validate task title.

    Rules:
    - Must not be empty after stripping whitespace
    - Length: 1-200 characters
    - Leading/trailing whitespace is trimmed

    Returns:
        (is_valid, error_message or cleaned_title)
    """
```

**Validation Logic:**
1. Strip leading/trailing whitespace
2. Check if empty → Error: "Title cannot be empty"
3. Check length > 200 → Error: "Title must be 200 characters or less"
4. Return cleaned title

### 2.2 Description Validation
```python
def validate_description(description: str) -> tuple[bool, str]:
    """
    Validate task description.

    Rules:
    - Optional (empty string allowed)
    - Maximum 1000 characters
    - Leading/trailing whitespace is trimmed

    Returns:
        (is_valid, error_message or cleaned_description)
    """
```

**Validation Logic:**
1. Strip leading/trailing whitespace
2. Check length > 1000 → Error: "Description must be 1000 characters or less"
3. Return cleaned description

### 2.3 ID Validation
```python
def validate_id(id_input: str, existing_ids: set[int]) -> tuple[bool, int | str]:
    """
    Validate task ID input.

    Rules:
    - Must be a valid positive integer
    - Must exist in the task list

    Returns:
        (is_valid, parsed_id or error_message)
    """
```

**Validation Logic:**
1. Try to parse as integer → Error: "Please enter a valid number"
2. Check if positive → Error: "ID must be a positive number"
3. Check if exists → Error: "Task with ID {id} not found"
4. Return parsed ID

---

## 3. Task Manager

### 3.1 Data Storage
```python
class TaskManager:
    """In-memory task storage and operations."""

    _tasks: dict[int, Task]  # ID → Task mapping
    _next_id: int            # Next available ID
```

### 3.2 Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Add | `add(title, description) → Task` | Create and store new task |
| Get All | `get_all() → list[Task]` | Return all tasks |
| Get One | `get(id) → Task | None` | Return task by ID |
| Update | `update(id, title?, description?) → bool` | Modify task |
| Delete | `delete(id) → bool` | Remove task |
| Toggle | `toggle_complete(id) → bool` | Toggle completion |

### 3.3 Method Specifications

#### `add(title: str, description: str = "") -> Task`
```
Preconditions:
  - title is validated
  - description is validated

Postconditions:
  - New Task created with auto-generated ID
  - Task stored in _tasks
  - _next_id incremented
  - Returns created Task

Side Effects:
  - Modifies _tasks
  - Increments _next_id
```

#### `get_all() -> list[Task]`
```
Preconditions:
  - None

Postconditions:
  - Returns list of all tasks
  - Returns empty list if no tasks
  - Original order preserved (by ID)

Side Effects:
  - None (read-only)
```

#### `get(id: int) -> Task | None`
```
Preconditions:
  - id is a positive integer

Postconditions:
  - Returns Task if found
  - Returns None if not found

Side Effects:
  - None (read-only)
```

#### `update(id: int, title: str | None = None, description: str | None = None) -> bool`
```
Preconditions:
  - id exists in _tasks
  - At least one of title/description provided
  - Provided values are validated

Postconditions:
  - Task fields updated
  - updated_at set to current time
  - Returns True on success

Side Effects:
  - Modifies task in _tasks
```

#### `delete(id: int) -> bool`
```
Preconditions:
  - id is a positive integer

Postconditions:
  - Task removed from _tasks if exists
  - Returns True if deleted
  - Returns False if not found

Side Effects:
  - May modify _tasks
```

#### `toggle_complete(id: int) -> bool`
```
Preconditions:
  - id exists in _tasks

Postconditions:
  - completed field toggled
  - updated_at set to current time
  - Returns True on success

Side Effects:
  - Modifies task in _tasks
```

---

## 4. Display Formatting

### 4.1 Task Display Format
```
[{status}] #{id}: {title}
    {description_preview}
    Created: {created_at_formatted}
```

Where:
- `{status}` = `x` if completed, ` ` if pending
- `{id}` = Task ID (padded for alignment)
- `{title}` = Full title
- `{description_preview}` = First 50 chars + "..." if longer
- `{created_at_formatted}` = "YYYY-MM-DD HH:MM"

### 4.2 Example Output
```
[ ] #1: Buy groceries
    Get milk, eggs, and bread from the store...
    Created: 2024-01-15 10:30

[x] #2: Call dentist
    Schedule annual checkup
    Created: 2024-01-14 09:15
```

---

## 5. Error Messages

| Scenario | Error Message |
|----------|---------------|
| Empty title | "Error: Title cannot be empty" |
| Title too long | "Error: Title must be 200 characters or less" |
| Description too long | "Error: Description must be 1000 characters or less" |
| Invalid ID format | "Error: Please enter a valid number" |
| ID not found | "Error: Task with ID {id} not found" |
| No tasks exist | "No tasks yet. Add one to get started!" |
