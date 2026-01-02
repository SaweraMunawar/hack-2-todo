# Feature Specification: Mark as Complete

## Feature ID: F5

## Overview
Allow users to toggle the completion status of a task.

---

## User Story
**As a** user
**I want to** mark tasks as complete or incomplete
**So that** I can track my progress

---

## Functional Requirements

### Inputs
| Field | Required | Validation |
|-------|----------|------------|
| Task ID | Yes | Must exist |

### Process Flow
```
1. User selects "Mark Complete" from menu
2. System displays current tasks with status
3. System prompts for task ID
4. User enters task ID
5. System validates ID
   - If invalid/not found: Show error, return to step 3
   - If valid: Continue
6. System toggles completion status:
   - If was pending → mark complete
   - If was complete → mark pending
7. System updates updated_at timestamp
8. System shows confirmation with new status
9. Return to main menu
```

### Outputs
- Success: Confirmation message with new status
- Failure: Error message describing the issue

---

## User Interface

### Initial Display
```
=== Mark Task Complete ===

Current tasks:
  [ ] #1: Buy groceries
  [x] #2: Call dentist
  [ ] #3: Finish report

Enter task ID to toggle: _
```

### Success Messages

#### Marking Complete
```
✓ Task #1 "Buy groceries" marked as COMPLETE.
```

#### Marking Incomplete
```
✓ Task #2 "Call dentist" marked as PENDING.
```

### Error Messages
```
✗ Error: Please enter a valid number

✗ Error: Task with ID 99 not found

✗ Error: No tasks available
```

---

## Toggle Behavior

### State Transitions
| Current State | New State | Message |
|---------------|-----------|---------|
| Pending (incomplete) | Complete | "marked as COMPLETE" |
| Complete | Pending (incomplete) | "marked as PENDING" |

### No Confirmation Required
- Toggle is a quick action
- No confirmation prompt needed
- Easy to undo by toggling again

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No tasks exist | Show "No tasks available" message |
| Invalid ID format | Show error, re-prompt |
| ID not found | Show error, re-prompt |
| Toggle pending → complete | Mark complete, show confirmation |
| Toggle complete → pending | Mark pending, show confirmation |
| Toggle same task twice | Returns to original state |
| User presses Ctrl+C | Return to main menu gracefully |

---

## Implementation Notes

### Timestamp Update
- Set `updated_at` to current time on toggle
- Preserves `created_at` unchanged

### Quick Access
- This is a frequently used action
- Keep the flow simple and fast
- No unnecessary confirmations

### Status Display
- After toggle, clearly show the NEW status
- Use visual distinction (COMPLETE vs PENDING)
