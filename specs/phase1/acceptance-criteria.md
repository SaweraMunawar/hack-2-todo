# Phase I Acceptance Criteria

## Document Information
- **Phase**: I - Todo In-Memory Python Console App
- **Version**: 1.0.0

---

## 1. Application Startup

### AC-1.1: Clean Start
```
GIVEN the application is installed correctly
WHEN the user runs `uv run python -m todo`
THEN the application starts without errors
AND displays the main menu
```

### AC-1.2: Menu Display
```
GIVEN the application has started
WHEN the main menu is displayed
THEN all 6 options are visible (1-5 features + 0 exit)
AND options are clearly labeled
AND a prompt awaits user input
```

---

## 2. Add Task (F1)

### AC-2.1: Add Task with Title Only
```
GIVEN the user is on the main menu
WHEN the user selects option 1 (Add Task)
AND enters a valid title "Buy groceries"
AND presses Enter for description (empty)
THEN a new task is created with:
  - Unique auto-incremented ID
  - Title: "Buy groceries"
  - Description: "" (empty)
  - Status: Pending
  - Created timestamp: current time
AND a success message is displayed
AND the user returns to the main menu
```

### AC-2.2: Add Task with Title and Description
```
GIVEN the user is on the main menu
WHEN the user selects option 1 (Add Task)
AND enters title "Call dentist"
AND enters description "Schedule annual checkup for next month"
THEN a new task is created with both title and description
AND a success message is displayed
```

### AC-2.3: Empty Title Validation
```
GIVEN the user is adding a task
WHEN the user enters an empty title (or only whitespace)
THEN an error message "Title cannot be empty" is displayed
AND the user is prompted to enter the title again
```

### AC-2.4: Title Length Validation
```
GIVEN the user is adding a task
WHEN the user enters a title longer than 200 characters
THEN an error message "Title must be 200 characters or less" is displayed
AND the user is prompted to enter the title again
```

### AC-2.5: Description Length Validation
```
GIVEN the user is adding a task
WHEN the user enters a description longer than 1000 characters
THEN an error message "Description must be 1000 characters or less" is displayed
AND the user is prompted to enter the description again
```

---

## 3. View Tasks (F2)

### AC-3.1: View Tasks - Empty List
```
GIVEN there are no tasks in the system
WHEN the user selects option 2 (View Tasks)
THEN a message "No tasks yet. Add one to get started!" is displayed
AND the user returns to the main menu
```

### AC-3.2: View Tasks - With Tasks
```
GIVEN there are 3 tasks in the system
WHEN the user selects option 2 (View Tasks)
THEN all 3 tasks are displayed
AND each task shows: ID, status indicator, title, description preview, created time
AND a summary shows "Total: 3 | Completed: X | Pending: Y"
```

### AC-3.3: Status Indicators
```
GIVEN there is a pending task and a completed task
WHEN the user views tasks
THEN pending tasks show "[ ]" indicator
AND completed tasks show "[x]" indicator
```

### AC-3.4: Description Truncation
```
GIVEN there is a task with a 100-character description
WHEN the user views tasks
THEN the description shows first 50 characters followed by "..."
```

---

## 4. Update Task (F3)

### AC-4.1: Update Title Only
```
GIVEN there is a task with ID #1, title "Buy grocries" (typo)
WHEN the user selects option 3 (Update Task)
AND enters ID "1"
AND enters new title "Buy groceries"
AND presses Enter to keep current description
THEN the task title is updated to "Buy groceries"
AND updated_at is set to current time
AND a success message is displayed
```

### AC-4.2: Update Description Only
```
GIVEN there is a task with ID #1
WHEN the user updates task #1
AND presses Enter to keep current title
AND enters new description "Get milk and eggs"
THEN the task description is updated
AND the title remains unchanged
AND updated_at is set to current time
```

### AC-4.3: Update Both Fields
```
GIVEN there is a task with ID #1
WHEN the user updates both title and description
THEN both fields are updated
AND a success message mentions both updated fields
```

### AC-4.4: No Changes Made
```
GIVEN there is a task with ID #1
WHEN the user updates task #1
AND presses Enter for both title and description (keeping current)
THEN a message "No changes made" is displayed
AND updated_at remains unchanged
```

### AC-4.5: Invalid Task ID
```
GIVEN the user is updating a task
WHEN the user enters a non-existent ID "99"
THEN an error message "Task with ID 99 not found" is displayed
AND the user is prompted to enter an ID again
```

### AC-4.6: No Tasks to Update
```
GIVEN there are no tasks in the system
WHEN the user selects option 3 (Update Task)
THEN a message "No tasks to update" is displayed
AND the user returns to the main menu
```

---

## 5. Delete Task (F4)

### AC-5.1: Delete with Confirmation
```
GIVEN there is a task with ID #1 "Buy groceries"
WHEN the user selects option 4 (Delete Task)
AND enters ID "1"
AND confirms with "y"
THEN the task is permanently deleted
AND a success message "Task #1 deleted successfully" is displayed
AND the task no longer appears in View Tasks
```

### AC-5.2: Cancel Deletion
```
GIVEN there is a task with ID #1
WHEN the user selects Delete Task
AND enters ID "1"
AND responds with "n" (or any non-yes input)
THEN the task is NOT deleted
AND a message "Deletion cancelled" is displayed
AND the task still exists
```

### AC-5.3: Default to Cancel
```
GIVEN the user is confirming deletion
WHEN the user presses Enter without typing anything
THEN the deletion is cancelled (default = No)
```

### AC-5.4: Invalid Task ID
```
GIVEN the user is deleting a task
WHEN the user enters a non-existent ID
THEN an error message is displayed
AND the user is prompted to enter an ID again
```

### AC-5.5: No Tasks to Delete
```
GIVEN there are no tasks in the system
WHEN the user selects option 4 (Delete Task)
THEN a message "No tasks to delete" is displayed
AND the user returns to the main menu
```

---

## 6. Mark Complete (F5)

### AC-6.1: Mark Pending as Complete
```
GIVEN there is a pending task with ID #1
WHEN the user selects option 5 (Mark Complete)
AND enters ID "1"
THEN the task status changes from pending to complete
AND a message "Task #1 marked as COMPLETE" is displayed
AND the task shows [x] in View Tasks
```

### AC-6.2: Mark Complete as Pending
```
GIVEN there is a completed task with ID #1
WHEN the user selects option 5 (Mark Complete)
AND enters ID "1"
THEN the task status changes from complete to pending
AND a message "Task #1 marked as PENDING" is displayed
AND the task shows [ ] in View Tasks
```

### AC-6.3: Toggle Updates Timestamp
```
GIVEN a task is toggled
THEN the updated_at field is set to current time
AND the created_at field remains unchanged
```

### AC-6.4: Invalid Task ID
```
GIVEN the user is marking a task complete
WHEN the user enters a non-existent ID
THEN an error message is displayed
AND the user is prompted to enter an ID again
```

---

## 7. Exit Application

### AC-7.1: Clean Exit via Menu
```
GIVEN the user is on the main menu
WHEN the user selects option 0 (Exit)
THEN a goodbye message is displayed
AND the application exits with code 0
```

### AC-7.2: Clean Exit via Ctrl+C
```
GIVEN the application is running
WHEN the user presses Ctrl+C
THEN the application exits gracefully
AND no stack trace is displayed
AND a brief goodbye message may be shown
```

---

## 8. Error Handling

### AC-8.1: Invalid Menu Choice
```
GIVEN the user is on the main menu
WHEN the user enters an invalid choice (e.g., "7", "abc", "")
THEN an error message "Invalid choice. Please try again." is displayed
AND the main menu is redisplayed
```

### AC-8.2: Non-Numeric ID Input
```
GIVEN the user is prompted for a task ID
WHEN the user enters non-numeric input (e.g., "abc")
THEN an error message "Please enter a valid number" is displayed
AND the user is prompted again
```

---

## 9. Data Integrity

### AC-9.1: Unique IDs
```
GIVEN multiple tasks are added
THEN each task has a unique ID
AND IDs increment sequentially (1, 2, 3, ...)
```

### AC-9.2: ID Not Reused
```
GIVEN tasks with IDs 1, 2, 3 exist
WHEN task #2 is deleted
AND a new task is added
THEN the new task gets ID 4 (not 2)
```

### AC-9.3: Data Preserved in Memory
```
GIVEN tasks are added during a session
WHEN the user views tasks multiple times
THEN all previously added tasks are still present
AND their data is unchanged
```

---

## 10. Test Commands Summary

```bash
# Start the application
uv run python -m todo

# Expected: Main menu appears with options 0-5

# Test each feature:
# 1 → Add Task (test valid/invalid inputs)
# 2 → View Tasks (test empty and populated)
# 3 → Update Task (test partial and full updates)
# 4 → Delete Task (test confirm and cancel)
# 5 → Mark Complete (test toggle both ways)
# 0 → Exit (verify clean shutdown)
```
