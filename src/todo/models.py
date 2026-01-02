"""Task data model and validation functions.

This module defines the Task dataclass and validation functions
as specified in specs/phase1/data-model.md.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represents a single todo task.

    Attributes:
        id: Unique identifier (auto-generated, positive integer)
        title: Task title (1-200 characters, required)
        description: Task description (0-1000 characters, optional)
        completed: Completion status (default: False)
        created_at: Creation timestamp (UTC)
        updated_at: Last modification timestamp (None until updated)
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = None


def validate_title(title: str) -> tuple[bool, str]:
    """Validate task title.

    Rules:
    - Must not be empty after stripping whitespace
    - Length: 1-200 characters
    - Leading/trailing whitespace is trimmed

    Args:
        title: The title string to validate

    Returns:
        tuple: (is_valid, error_message or cleaned_title)
            - If valid: (True, cleaned_title)
            - If invalid: (False, error_message)
    """
    cleaned = title.strip()

    if not cleaned:
        return (False, "Title cannot be empty")

    if len(cleaned) > 200:
        return (False, "Title must be 200 characters or less")

    return (True, cleaned)


def validate_description(description: str) -> tuple[bool, str]:
    """Validate task description.

    Rules:
    - Optional (empty string allowed)
    - Maximum 1000 characters
    - Leading/trailing whitespace is trimmed

    Args:
        description: The description string to validate

    Returns:
        tuple: (is_valid, error_message or cleaned_description)
            - If valid: (True, cleaned_description)
            - If invalid: (False, error_message)
    """
    cleaned = description.strip()

    if len(cleaned) > 1000:
        return (False, "Description must be 1000 characters or less")

    return (True, cleaned)


def validate_id(id_input: str, existing_ids: set[int]) -> tuple[bool, int | str]:
    """Validate task ID input.

    Rules:
    - Must be a valid positive integer
    - Must exist in the task list

    Args:
        id_input: The ID string to validate
        existing_ids: Set of existing task IDs

    Returns:
        tuple: (is_valid, parsed_id or error_message)
            - If valid: (True, parsed_id as int)
            - If invalid: (False, error_message)
    """
    # Try to parse as integer
    try:
        parsed_id = int(id_input.strip())
    except ValueError:
        return (False, "Please enter a valid number")

    # Check if positive
    if parsed_id <= 0:
        return (False, "ID must be a positive number")

    # Check if exists
    if parsed_id not in existing_ids:
        return (False, f"Task with ID {parsed_id} not found")

    return (True, parsed_id)
