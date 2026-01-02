# Feature Specification: Update Task

## Feature ID: F3

## Overview
Allow users to modify the title and/or description of an existing task.

---

## User Story
**As a** user
**I want to** edit my existing tasks
**So that** I can fix mistakes or update task details

---

## Functional Requirements

### Inputs
| Field | Required | Validation |
|-------|----------|------------|
| Task ID | Yes | Must exist |
| New Title | No | 1-200 characters if provided |
| New Description | No | 0-1000 characters if provided |

### Process Flow
```
1. User selects "Update Task" from menu
2. System displays current tasks (brief list)
3. System prompts for task ID
4. User enters task ID
5. System validates ID
   - If invalid/not found: Show error, return to step 3
   - If valid: Continue
6. System shows current task details
7. System prompts for new title (Enter to keep current)
8. User enters new title or presses Enter
9. If new title provided:
   - Validate title
   - If invalid: Show error, return to step 7
10. System prompts for new description (Enter to keep current)
11. User enters new description or presses Enter
12. If new description provided:
    - Validate description
    - If invalid: Show error, return to step 10
13. If no changes made:
    - Show "No changes made" message
14. If changes made:
    - Update task
    - Set updated_at to current time
    - Show success message
15. Return to main menu
```

### Outputs
- Success: Confirmation message showing updated fields
- No changes: Informational message
- Failure: Error message describing the issue

---

## User Interface

### Initial Display
```
=== Update Task ===

Current tasks:
  #1: Buy groceries
  #2: Call dentist
  #3: Finish report

Enter task ID to update: _
```

### Current Task Display
```
Editing Task #1:
  Title: Buy groceries
  Description: Get milk, eggs, and bread from the store
  Status: Pending
  Created: 2024-01-15 10:30
```

### Update Prompts
```
Enter new title (press Enter to keep current): _

Enter new description (press Enter to keep current): _
```

### Success Message
```
✓ Task #1 updated successfully!
  Updated fields: title, description
```

### No Changes Message
```
ℹ No changes made to Task #1.
```

### Error Messages
```
✗ Error: Please enter a valid number

✗ Error: Task with ID 99 not found

✗ Error: Title cannot be empty

✗ Error: Title must be 200 characters or less
```

---

## Special Behaviors

### Keep Current Value
- Press Enter with no input → keep existing value
- This applies to both title and description
- At least one field must have a new value OR user explicitly keeps both

### Clear Description
- Enter a single space or "clear" → set description to empty
- Alternatively, support "(clear)" as input

### Updated Timestamp
- Only set `updated_at` if actual changes are made
- Use current UTC time

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No tasks exist | Show message "No tasks to update" |
| Invalid ID format | Show error, re-prompt |
| ID not found | Show error, re-prompt |
| Keep both values | Show "No changes made" |
| Update title only | Update title, keep description |
| Update description only | Keep title, update description |
| Clear description | Set description to empty string |
| User presses Ctrl+C | Return to main menu gracefully |
