"""Main entry point for the Todo Console Application.

This module implements the main application loop and all feature workflows
as specified in specs/phase1/features/*.md.
"""

import sys

from .manager import TaskManager
from .models import validate_description, validate_id, validate_title
from .ui import (
    confirm,
    format_task_detail,
    get_input,
    get_input_keep_current,
    get_input_optional,
    get_validated_input,
    show_error,
    show_header,
    show_info,
    show_menu,
    show_success,
    show_task_list,
    show_task_list_brief,
    show_warning,
)


class TodoApp:
    """Main application class for the console todo app.

    Handles the main menu loop and routes to feature methods.
    """

    def __init__(self) -> None:
        """Initialize the application."""
        self.manager = TaskManager()
        self.running = True

    def run(self) -> None:
        """Main application loop."""
        try:
            while self.running:
                show_menu()
                self._handle_menu_choice()
        except KeyboardInterrupt:
            print()
            show_info("Goodbye!")
            sys.exit(0)
        except EOFError:
            print()
            show_info("Goodbye!")
            sys.exit(0)

    def _handle_menu_choice(self) -> None:
        """Handle user menu selection."""
        choice = get_input("Enter your choice")

        actions = {
            "1": self._add_task,
            "2": self._view_tasks,
            "3": self._update_task,
            "4": self._delete_task,
            "5": self._mark_complete,
            "0": self._exit,
        }

        action = actions.get(choice)
        if action:
            action()
        else:
            show_error("Invalid choice. Please try again.")

    def _add_task(self) -> None:
        """Add a new task (Feature F1).

        Workflow:
        1. Prompt for title (required)
        2. Validate title
        3. Prompt for description (optional)
        4. Validate description
        5. Create task
        6. Show confirmation
        """
        show_header("Add New Task")

        # Get and validate title
        title = get_validated_input("Enter task title", validate_title)

        # Get and validate description (optional)
        desc_input = get_input_optional("description")
        is_valid, result = validate_description(desc_input)
        if not is_valid:
            show_error(result)
            return

        # Create the task
        task = self.manager.add(title, result)

        # Show confirmation
        show_success("Task added successfully!")
        print(f"  ID: #{task.id}")
        print(f"  Title: {task.title}")

    def _view_tasks(self) -> None:
        """View all tasks (Feature F2).

        Workflow:
        1. Get all tasks
        2. Display in full format
        3. Show summary
        """
        show_header("Your Tasks")

        tasks = self.manager.get_all()
        show_task_list(tasks, show_summary=True)

    def _update_task(self) -> None:
        """Update an existing task (Feature F3).

        Workflow:
        1. Check for empty list
        2. Show current tasks
        3. Prompt for task ID
        4. Show current task details
        5. Prompt for new title (Enter to keep)
        6. Prompt for new description (Enter to keep)
        7. Apply changes if any
        8. Show confirmation
        """
        show_header("Update Task")

        # Check for empty list
        if self.manager.is_empty():
            show_info("No tasks to update.")
            return

        # Show current tasks
        tasks = self.manager.get_all()
        show_task_list_brief(tasks)

        # Get and validate task ID
        existing_ids = self.manager.get_ids()

        def validate_existing_id(id_input: str) -> tuple[bool, str]:
            is_valid, result = validate_id(id_input, existing_ids)
            if is_valid:
                return (True, str(result))
            return (False, result)

        task_id_str = get_validated_input("Enter task ID to update", validate_existing_id)
        task_id = int(task_id_str)

        # Get current task
        task = self.manager.get(task_id)
        if not task:
            show_error(f"Task with ID {task_id} not found")
            return

        # Show current details
        print(f"\nEditing Task #{task_id}:")
        print(format_task_detail(task))
        print()

        # Get new title (optional)
        new_title_input = get_input_keep_current("title", task.title)
        new_title = None
        if new_title_input:
            is_valid, result = validate_title(new_title_input)
            if not is_valid:
                show_error(result)
                return
            new_title = result

        # Get new description (optional)
        new_desc_input = get_input_keep_current("description", task.description)
        new_description = None
        if new_desc_input:
            is_valid, result = validate_description(new_desc_input)
            if not is_valid:
                show_error(result)
                return
            new_description = result

        # Check if any changes
        if new_title is None and new_description is None:
            show_info(f"No changes made to Task #{task_id}.")
            return

        # Apply updates
        self.manager.update(task_id, title=new_title, description=new_description)

        # Show confirmation
        updated_fields = []
        if new_title is not None:
            updated_fields.append("title")
        if new_description is not None:
            updated_fields.append("description")

        show_success(f"Task #{task_id} updated successfully!")
        print(f"  Updated fields: {', '.join(updated_fields)}")

    def _delete_task(self) -> None:
        """Delete a task (Feature F4).

        Workflow:
        1. Check for empty list
        2. Show current tasks
        3. Prompt for task ID
        4. Show task details
        5. Confirm deletion
        6. Delete if confirmed
        7. Show result
        """
        show_header("Delete Task")

        # Check for empty list
        if self.manager.is_empty():
            show_info("No tasks to delete.")
            return

        # Show current tasks
        tasks = self.manager.get_all()
        show_task_list_brief(tasks)

        # Get and validate task ID
        existing_ids = self.manager.get_ids()

        def validate_existing_id(id_input: str) -> tuple[bool, str]:
            is_valid, result = validate_id(id_input, existing_ids)
            if is_valid:
                return (True, str(result))
            return (False, result)

        task_id_str = get_validated_input("Enter task ID to delete", validate_existing_id)
        task_id = int(task_id_str)

        # Get and display task
        task = self.manager.get(task_id)
        if not task:
            show_error(f"Task with ID {task_id} not found")
            return

        print("\nYou are about to delete:")
        print(format_task_detail(task))
        print()
        show_warning("This action cannot be undone.")
        print()

        # Confirm deletion (default = No)
        if not confirm("Delete this task?", default=False):
            show_info(f"Deletion cancelled. Task #{task_id} was not deleted.")
            return

        # Delete the task
        self.manager.delete(task_id)
        show_success(f'Task #{task_id} "{task.title}" deleted successfully.')

    def _mark_complete(self) -> None:
        """Toggle task completion status (Feature F5).

        Workflow:
        1. Check for empty list
        2. Show current tasks with status
        3. Prompt for task ID
        4. Toggle status
        5. Show confirmation with new status
        """
        show_header("Mark Task Complete")

        # Check for empty list
        if self.manager.is_empty():
            show_info("No tasks available.")
            return

        # Show current tasks
        tasks = self.manager.get_all()
        show_task_list_brief(tasks)

        # Get and validate task ID
        existing_ids = self.manager.get_ids()

        def validate_existing_id(id_input: str) -> tuple[bool, str]:
            is_valid, result = validate_id(id_input, existing_ids)
            if is_valid:
                return (True, str(result))
            return (False, result)

        task_id_str = get_validated_input("Enter task ID to toggle", validate_existing_id)
        task_id = int(task_id_str)

        # Get task before toggle
        task = self.manager.get(task_id)
        if not task:
            show_error(f"Task with ID {task_id} not found")
            return

        # Toggle completion
        self.manager.toggle_complete(task_id)

        # Show confirmation with new status
        new_status = "COMPLETE" if task.completed else "PENDING"
        show_success(f'Task #{task_id} "{task.title}" marked as {new_status}.')

    def _exit(self) -> None:
        """Exit the application."""
        self.running = False
        show_info("Goodbye!")


def main() -> None:
    """Entry point for the application."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
