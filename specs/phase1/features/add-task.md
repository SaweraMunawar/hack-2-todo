# Feature Specification: Add Task

## Feature ID: F1

## Overview
Allow users to create new todo items with a title and optional description.

---

## User Story
**As a** user
**I want to** add new tasks to my todo list
**So that** I can track things I need to do

---

## Functional Requirements

### Inputs
| Field | Required | Validation |
|-------|----------|------------|
| Title | Yes | 1-200 characters, non-empty |
| Description | No | 0-1000 characters |

### Process Flow
```
1. User selects "Add Task" from menu
2. System prompts for title
3. User enters title
4. System validates title
   - If invalid: Show error, return to step 2
   - If valid: Continue
5. System prompts for description (optional)
6. User enters description or presses Enter to skip
7. System validates description
   - If invalid: Show error, return to step 5
   - If valid: Continue
8. System creates task with:
   - Auto-generated unique ID
   - Provided title (trimmed)
   - Provided description (trimmed) or empty string
   - completed = False
   - created_at = current timestamp
   - updated_at = None
9. System displays confirmation message
10. Return to main menu
```

### Outputs
- Success: Confirmation message with task ID and title
- Failure: Error message describing the validation issue

---

## User Interface

### Prompts
```
=== Add New Task ===

Enter task title: _

Enter description (optional, press Enter to skip): _
```

### Success Message
```
✓ Task added successfully!
  ID: #1
  Title: Buy groceries
```

### Error Messages
```
✗ Error: Title cannot be empty

✗ Error: Title must be 200 characters or less

✗ Error: Description must be 1000 characters or less
```

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty title (just spaces) | Show error, re-prompt |
| Title exactly 200 chars | Accept |
| Title with 201 chars | Show error, re-prompt |
| Empty description | Accept (set to empty string) |
| Description exactly 1000 chars | Accept |
| User presses Ctrl+C | Return to main menu gracefully |

---

## Implementation Notes

### ID Generation
- Start from 1
- Increment for each new task
- Never reuse deleted IDs (simple counter)

### Timestamp
- Use UTC timezone
- Store as datetime object
- Format for display: "YYYY-MM-DD HH:MM"

### Input Handling
- Strip whitespace from both title and description
- Preserve internal whitespace and formatting
