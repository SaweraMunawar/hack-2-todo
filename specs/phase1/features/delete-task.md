# Feature Specification: Delete Task

## Feature ID: F4

## Overview
Allow users to permanently remove a task from the list.

---

## User Story
**As a** user
**I want to** delete tasks I no longer need
**So that** my todo list stays clean and relevant

---

## Functional Requirements

### Inputs
| Field | Required | Validation |
|-------|----------|------------|
| Task ID | Yes | Must exist |
| Confirmation | Yes | Must be 'y' or 'yes' |

### Process Flow
```
1. User selects "Delete Task" from menu
2. System displays current tasks (brief list)
3. System prompts for task ID
4. User enters task ID
5. System validates ID
   - If invalid/not found: Show error, return to step 3
   - If valid: Continue
6. System shows task details
7. System asks for confirmation
8. User responds:
   - If 'y' or 'yes': Delete task, show success
   - If any other input: Cancel, show cancelled message
9. Return to main menu
```

### Outputs
- Success: Confirmation message with deleted task info
- Cancelled: Informational message
- Failure: Error message describing the issue

---

## User Interface

### Initial Display
```
=== Delete Task ===

Current tasks:
  #1: Buy groceries [pending]
  #2: Call dentist [completed]
  #3: Finish report [pending]

Enter task ID to delete: _
```

### Confirmation Prompt
```
You are about to delete:
  #1: Buy groceries
  Status: Pending
  Created: 2024-01-15 10:30

⚠ This action cannot be undone.

Delete this task? (y/N): _
```

### Success Message
```
✓ Task #1 "Buy groceries" deleted successfully.
```

### Cancelled Message
```
ℹ Deletion cancelled. Task #1 was not deleted.
```

### Error Messages
```
✗ Error: Please enter a valid number

✗ Error: Task with ID 99 not found

✗ Error: No tasks to delete
```

---

## Confirmation Rules

### Accepted Confirmations
| Input | Result |
|-------|--------|
| `y` | Delete |
| `Y` | Delete |
| `yes` | Delete |
| `YES` | Delete |
| `Yes` | Delete |

### Rejected Confirmations
| Input | Result |
|-------|--------|
| `n` | Cancel |
| `no` | Cancel |
| `N` | Cancel |
| (empty/Enter) | Cancel |
| Any other text | Cancel |

### Default Behavior
- Default is **No** (safe option)
- Shown as `(y/N)` with capital N

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No tasks exist | Show "No tasks to delete" message |
| Invalid ID format | Show error, re-prompt for ID |
| ID not found | Show error, re-prompt for ID |
| User confirms deletion | Delete task, show success |
| User cancels | Keep task, show cancelled message |
| User presses Ctrl+C during confirmation | Cancel gracefully |
| Delete last remaining task | Allow, list becomes empty |

---

## Implementation Notes

### Confirmation Safety
- Always require explicit confirmation
- Never auto-confirm deletions
- Show full task details before confirming

### Post-Deletion
- Task is immediately removed from memory
- ID is not reused
- Other task IDs are not affected
