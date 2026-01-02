"""Tests for Task model and validation functions."""

import pytest
from datetime import datetime

from todo.models import Task, validate_title, validate_description, validate_id


class TestTask:
    """Tests for the Task dataclass."""

    def test_create_task_with_defaults(self):
        """Test creating a task with default values."""
        task = Task(id=1, title="Test task")
        assert task.id == 1
        assert task.title == "Test task"
        assert task.description == ""
        assert task.completed is False
        assert isinstance(task.created_at, datetime)
        assert task.updated_at is None

    def test_create_task_with_all_fields(self):
        """Test creating a task with all fields specified."""
        now = datetime.now()
        task = Task(
            id=1,
            title="Test task",
            description="A description",
            completed=True,
            created_at=now,
            updated_at=now,
        )
        assert task.id == 1
        assert task.title == "Test task"
        assert task.description == "A description"
        assert task.completed is True
        assert task.created_at == now
        assert task.updated_at == now


class TestValidateTitle:
    """Tests for title validation."""

    def test_valid_title(self):
        """Test valid title returns success."""
        is_valid, result = validate_title("Buy groceries")
        assert is_valid is True
        assert result == "Buy groceries"

    def test_title_strips_whitespace(self):
        """Test that whitespace is trimmed."""
        is_valid, result = validate_title("  Buy groceries  ")
        assert is_valid is True
        assert result == "Buy groceries"

    def test_empty_title_fails(self):
        """Test that empty title returns error."""
        is_valid, result = validate_title("")
        assert is_valid is False
        assert result == "Title cannot be empty"

    def test_whitespace_only_title_fails(self):
        """Test that whitespace-only title returns error."""
        is_valid, result = validate_title("   ")
        assert is_valid is False
        assert result == "Title cannot be empty"

    def test_title_at_max_length(self):
        """Test title at exactly 200 characters is valid."""
        title = "a" * 200
        is_valid, result = validate_title(title)
        assert is_valid is True
        assert result == title

    def test_title_exceeds_max_length(self):
        """Test title over 200 characters returns error."""
        title = "a" * 201
        is_valid, result = validate_title(title)
        assert is_valid is False
        assert result == "Title must be 200 characters or less"


class TestValidateDescription:
    """Tests for description validation."""

    def test_valid_description(self):
        """Test valid description returns success."""
        is_valid, result = validate_description("A task description")
        assert is_valid is True
        assert result == "A task description"

    def test_empty_description_valid(self):
        """Test that empty description is valid."""
        is_valid, result = validate_description("")
        assert is_valid is True
        assert result == ""

    def test_description_strips_whitespace(self):
        """Test that whitespace is trimmed."""
        is_valid, result = validate_description("  Description  ")
        assert is_valid is True
        assert result == "Description"

    def test_description_at_max_length(self):
        """Test description at exactly 1000 characters is valid."""
        desc = "a" * 1000
        is_valid, result = validate_description(desc)
        assert is_valid is True
        assert result == desc

    def test_description_exceeds_max_length(self):
        """Test description over 1000 characters returns error."""
        desc = "a" * 1001
        is_valid, result = validate_description(desc)
        assert is_valid is False
        assert result == "Description must be 1000 characters or less"


class TestValidateId:
    """Tests for ID validation."""

    def test_valid_id(self):
        """Test valid ID returns success."""
        existing = {1, 2, 3}
        is_valid, result = validate_id("2", existing)
        assert is_valid is True
        assert result == 2

    def test_id_strips_whitespace(self):
        """Test that whitespace is trimmed."""
        existing = {1, 2, 3}
        is_valid, result = validate_id("  2  ", existing)
        assert is_valid is True
        assert result == 2

    def test_non_numeric_id_fails(self):
        """Test that non-numeric ID returns error."""
        existing = {1, 2, 3}
        is_valid, result = validate_id("abc", existing)
        assert is_valid is False
        assert result == "Please enter a valid number"

    def test_zero_id_fails(self):
        """Test that zero ID returns error."""
        existing = {1, 2, 3}
        is_valid, result = validate_id("0", existing)
        assert is_valid is False
        assert result == "ID must be a positive number"

    def test_negative_id_fails(self):
        """Test that negative ID returns error."""
        existing = {1, 2, 3}
        is_valid, result = validate_id("-1", existing)
        assert is_valid is False
        assert result == "ID must be a positive number"

    def test_nonexistent_id_fails(self):
        """Test that nonexistent ID returns error."""
        existing = {1, 2, 3}
        is_valid, result = validate_id("99", existing)
        assert is_valid is False
        assert result == "Task with ID 99 not found"

    def test_empty_existing_ids(self):
        """Test validation with empty existing IDs set."""
        existing = set()
        is_valid, result = validate_id("1", existing)
        assert is_valid is False
        assert result == "Task with ID 1 not found"
