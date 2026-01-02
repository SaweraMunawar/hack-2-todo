# Feature Specification: View Task List

## Feature ID: F2

## Overview
Display all tasks in a formatted, readable list with status indicators.

---

## User Story
**As a** user
**I want to** see all my tasks at a glance
**So that** I can understand what needs to be done

---

## Functional Requirements

### Inputs
None (displays all tasks)

### Process Flow
```
1. User selects "View Tasks" from menu
2. System retrieves all tasks
3. If no tasks exist:
   - Display "No tasks" message
4. If tasks exist:
   - Display header
   - Display each task with formatting
   - Display summary count
5. Return to main menu
```

### Outputs
- Formatted list of all tasks
- Each task shows: ID, status, title, description preview, created time
- Summary count of total/completed/pending

---

## User Interface

### Header
```
=== Your Tasks ===
```

### Task Display Format
```
[ ] #1: Buy groceries
    Get milk, eggs, and bread from the store...
    Created: 2024-01-15 10:30

[x] #2: Call dentist
    Schedule annual checkup
    Created: 2024-01-14 09:15
```

### Status Indicators
| Status | Indicator |
|--------|-----------|
| Pending | `[ ]` |
| Completed | `[x]` |

### Summary Footer
```
───────────────────────────────
Total: 5 | Completed: 2 | Pending: 3
```

### Empty State
```
=== Your Tasks ===

No tasks yet. Add one to get started!
```

---

## Display Rules

### Description Preview
- Show first 50 characters
- Add "..." if description is longer than 50 chars
- If empty, don't show description line

### Task Ordering
- Display in order of creation (by ID, ascending)
- Newest tasks appear at the bottom

### Formatting
- Indent description under title (4 spaces)
- Indent created time under title (4 spaces)
- Blank line between tasks for readability

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No tasks | Show empty state message |
| 1 task | Show single task, singular count |
| 100+ tasks | Show all tasks (no pagination) |
| Very long title | Show full title (no truncation) |
| No description | Omit description line |
| Very long description | Truncate to 50 chars + "..." |

---

## Implementation Notes

### Timestamp Formatting
```python
created_at.strftime("%Y-%m-%d %H:%M")
```

### Description Truncation
```python
def truncate(text: str, max_length: int = 50) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
```
