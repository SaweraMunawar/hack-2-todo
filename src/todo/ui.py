"""User interface formatting and display utilities.

This module provides all UI-related functions for the console application
as specified in specs/phase1/ui-spec.md.
"""

from typing import Callable

from .models import Task

# Box drawing characters
BOX_TL = "╔"
BOX_TR = "╗"
BOX_BL = "╚"
BOX_BR = "╝"
BOX_H = "═"
BOX_V = "║"
BOX_ML = "╠"
BOX_MR = "╣"

# Status indicators
STATUS_PENDING = "[ ]"
STATUS_COMPLETE = "[x]"

# Message icons
ICON_SUCCESS = "✓"
ICON_ERROR = "✗"
ICON_INFO = "ℹ"
ICON_WARNING = "⚠"

# Menu width
MENU_WIDTH = 40


def show_menu() -> None:
    """Display the main menu."""
    inner = MENU_WIDTH - 2
    title = "TODO APP - Phase I"

    print()
    print(f"{BOX_TL}{BOX_H * inner}{BOX_TR}")
    print(f"{BOX_V}{title:^{inner}}{BOX_V}")
    print(f"{BOX_ML}{BOX_H * inner}{BOX_MR}")
    print(f"{BOX_V}{' ' * inner}{BOX_V}")
    print(f"{BOX_V}{'   1. Add Task':<{inner}}{BOX_V}")
    print(f"{BOX_V}{'   2. View Tasks':<{inner}}{BOX_V}")
    print(f"{BOX_V}{'   3. Update Task':<{inner}}{BOX_V}")
    print(f"{BOX_V}{'   4. Delete Task':<{inner}}{BOX_V}")
    print(f"{BOX_V}{'   5. Mark Complete':<{inner}}{BOX_V}")
    print(f"{BOX_V}{'   0. Exit':<{inner}}{BOX_V}")
    print(f"{BOX_V}{' ' * inner}{BOX_V}")
    print(f"{BOX_BL}{BOX_H * inner}{BOX_BR}")
    print()


def show_header(title: str) -> None:
    """Display a section header.

    Args:
        title: The section title to display
    """
    print(f"\n=== {title} ===\n")


def show_success(message: str) -> None:
    """Display a success message.

    Args:
        message: The success message to display
    """
    print(f"{ICON_SUCCESS} {message}")


def show_error(message: str) -> None:
    """Display an error message.

    Args:
        message: The error message to display
    """
    print(f"{ICON_ERROR} Error: {message}")


def show_info(message: str) -> None:
    """Display an informational message.

    Args:
        message: The info message to display
    """
    print(f"{ICON_INFO} {message}")


def show_warning(message: str) -> None:
    """Display a warning message.

    Args:
        message: The warning message to display
    """
    print(f"{ICON_WARNING} {message}")


def show_separator() -> None:
    """Display a horizontal separator line."""
    print("─" * 35)


def truncate(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long.

    Args:
        text: The text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text with "..." if needed
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_datetime(dt) -> str:
    """Format a datetime for display.

    Args:
        dt: datetime object to format

    Returns:
        Formatted string "YYYY-MM-DD HH:MM"
    """
    return dt.strftime("%Y-%m-%d %H:%M")


def format_task_brief(task: Task) -> str:
    """Format a task for brief display (selection lists).

    Format: "  #1: Buy groceries [pending]"

    Args:
        task: The task to format

    Returns:
        Formatted task string
    """
    status = "completed" if task.completed else "pending"
    return f"  #{task.id}: {task.title} [{status}]"


def format_task_full(task: Task) -> str:
    """Format a task for full display.

    Format:
        [ ] #1: Buy groceries
            Get milk, eggs, and bread...
            Created: 2024-01-15 10:30

    Args:
        task: The task to format

    Returns:
        Formatted task string with multiple lines
    """
    status = STATUS_COMPLETE if task.completed else STATUS_PENDING
    lines = [f"{status} #{task.id}: {task.title}"]

    if task.description:
        desc_preview = truncate(task.description, 50)
        lines.append(f"    {desc_preview}")

    lines.append(f"    Created: {format_datetime(task.created_at)}")

    return "\n".join(lines)


def format_task_detail(task: Task) -> str:
    """Format a task for detailed display (confirmation).

    Format:
        #1: Buy groceries
        Description: Get milk, eggs, and bread
        Status: Pending
        Created: 2024-01-15 10:30

    Args:
        task: The task to format

    Returns:
        Formatted task string with all details
    """
    status = "Completed" if task.completed else "Pending"
    lines = [
        f"  #{task.id}: {task.title}",
        f"  Description: {task.description or '(none)'}",
        f"  Status: {status}",
        f"  Created: {format_datetime(task.created_at)}",
    ]
    return "\n".join(lines)


def show_task_list(tasks: list[Task], show_summary: bool = True) -> None:
    """Display a list of tasks in full format.

    Args:
        tasks: List of tasks to display
        show_summary: Whether to show the summary footer
    """
    if not tasks:
        print("\nNo tasks yet. Add one to get started!\n")
        return

    print()
    for task in tasks:
        print(format_task_full(task))
        print()

    if show_summary:
        total = len(tasks)
        completed = sum(1 for t in tasks if t.completed)
        pending = total - completed
        show_separator()
        print(f"Total: {total} | Completed: {completed} | Pending: {pending}")
        print()


def show_task_list_brief(tasks: list[Task]) -> None:
    """Display a list of tasks in brief format.

    Args:
        tasks: List of tasks to display
    """
    if not tasks:
        print("\nNo tasks yet. Add one to get started!\n")
        return

    print("\nCurrent tasks:")
    for task in tasks:
        print(format_task_brief(task))
    print()


def get_input(prompt: str) -> str:
    """Get input from the user.

    Args:
        prompt: The prompt to display

    Returns:
        User input string (stripped)
    """
    return input(f"{prompt}: ").strip()


def get_input_optional(prompt: str) -> str:
    """Get optional input from the user.

    Args:
        prompt: The field name

    Returns:
        User input string (stripped), may be empty
    """
    return input(f"Enter {prompt} (optional, press Enter to skip): ").strip()


def get_input_keep_current(prompt: str, current: str) -> str:
    """Get input with option to keep current value.

    Args:
        prompt: The field name
        current: The current value

    Returns:
        User input string or empty if keeping current
    """
    display_current = truncate(current, 30) if current else "(none)"
    return input(f'Enter new {prompt} (press Enter to keep "{display_current}"): ').strip()


def get_validated_input(
    prompt: str,
    validator: Callable[[str], tuple[bool, str]],
    allow_empty: bool = False,
) -> str:
    """Get input with validation and retry.

    Args:
        prompt: The prompt to display
        validator: Function that returns (is_valid, result_or_error)
        allow_empty: Whether empty input is allowed

    Returns:
        Validated input string
    """
    while True:
        value = input(f"{prompt}: ").strip()

        if not value and allow_empty:
            return ""

        is_valid, result = validator(value)
        if is_valid:
            return result
        show_error(result)


def confirm(prompt: str, default: bool = False) -> bool:
    """Ask for confirmation.

    Args:
        prompt: The question to ask
        default: Default value if user just presses Enter

    Returns:
        True if confirmed, False otherwise
    """
    suffix = "(Y/n)" if default else "(y/N)"
    response = input(f"{prompt} {suffix}: ").strip().lower()

    if not response:
        return default

    return response in ("y", "yes")


def pause() -> None:
    """Pause and wait for user to press Enter."""
    input("\nPress Enter to continue...")
