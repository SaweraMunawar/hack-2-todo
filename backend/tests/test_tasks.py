"""Tests for task CRUD endpoints."""

import jwt
import pytest

from todo_api.auth.jwt import CurrentUser
from todo_api.config import settings

TEST_USER = CurrentUser(id="test-user-id-123", email="test@example.com")
TEST_USER_2 = CurrentUser(id="test-user-id-456", email="other@example.com")


def make_auth_header(user: CurrentUser = TEST_USER) -> dict:
    """Create an Authorization header with a valid JWT for the given user."""
    payload = {"sub": user.id, "email": user.email}
    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def test_health_check(client):
    """AC-21: Health check returns healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_task(client):
    """AC-6: Create a task with valid data."""
    headers = make_auth_header()
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Buy groceries", "description": "Milk, eggs, bread"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_create_task_title_only(client):
    """Create a task with title only (description optional)."""
    headers = make_auth_header()
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Simple task"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Simple task"
    assert data["description"] == ""


def test_create_task_empty_title_fails(client):
    """AC-20: Validation error for empty title."""
    headers = make_auth_header()
    response = client.post(
        "/api/v1/tasks",
        json={"title": ""},
        headers=headers,
    )
    assert response.status_code == 422


def test_create_task_no_auth_fails(client):
    """AC-5: Unauthenticated requests return 401/403."""
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Unauthorized task"},
    )
    assert response.status_code in (401, 403)


def test_list_tasks(client):
    """AC-7: List tasks for authenticated user."""
    headers = make_auth_header()
    # Create two tasks
    client.post("/api/v1/tasks", json={"title": "Task 1"}, headers=headers)
    client.post("/api/v1/tasks", json={"title": "Task 2"}, headers=headers)

    response = client.get("/api/v1/tasks", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["tasks"]) == 2


def test_list_tasks_filter_completed(client):
    """AC-7: Filter tasks by completion status."""
    headers = make_auth_header()
    # Create a task and toggle it
    resp = client.post("/api/v1/tasks", json={"title": "Done task"}, headers=headers)
    task_id = resp.json()["id"]
    client.post(f"/api/v1/tasks/{task_id}/toggle", headers=headers)

    client.post("/api/v1/tasks", json={"title": "Pending task"}, headers=headers)

    # Filter completed
    response = client.get("/api/v1/tasks?completed=true", headers=headers)
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["completed"] is True

    # Filter pending
    response = client.get("/api/v1/tasks?completed=false", headers=headers)
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["completed"] is False


def test_get_task(client):
    """AC-7: Get a specific task by ID."""
    headers = make_auth_header()
    resp = client.post("/api/v1/tasks", json={"title": "My task"}, headers=headers)
    task_id = resp.json()["id"]

    response = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "My task"


def test_get_task_not_found(client):
    """AC-20: 404 for non-existent task."""
    headers = make_auth_header()
    response = client.get(
        "/api/v1/tasks/00000000-0000-0000-0000-000000000000", headers=headers
    )
    assert response.status_code == 404


def test_update_task(client):
    """AC-8: Update task title and description."""
    headers = make_auth_header()
    resp = client.post(
        "/api/v1/tasks",
        json={"title": "Original", "description": "Old desc"},
        headers=headers,
    )
    task_id = resp.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated", "description": "New desc"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["description"] == "New desc"
    assert data["updated_at"] is not None


def test_update_task_partial(client):
    """AC-8: Partial update - only title."""
    headers = make_auth_header()
    resp = client.post(
        "/api/v1/tasks",
        json={"title": "Original", "description": "Keep me"},
        headers=headers,
    )
    task_id = resp.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "New title"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["description"] == "Keep me"


def test_delete_task(client):
    """AC-9: Delete a task."""
    headers = make_auth_header()
    resp = client.post("/api/v1/tasks", json={"title": "Delete me"}, headers=headers)
    task_id = resp.json()["id"]

    response = client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert response.status_code == 404


def test_toggle_task(client):
    """AC-10: Toggle task completion."""
    headers = make_auth_header()
    resp = client.post("/api/v1/tasks", json={"title": "Toggle me"}, headers=headers)
    task_id = resp.json()["id"]
    assert resp.json()["completed"] is False

    # Toggle to completed
    response = client.post(f"/api/v1/tasks/{task_id}/toggle", headers=headers)
    assert response.status_code == 200
    assert response.json()["completed"] is True

    # Toggle back to pending
    response = client.post(f"/api/v1/tasks/{task_id}/toggle", headers=headers)
    assert response.status_code == 200
    assert response.json()["completed"] is False


def test_data_isolation(client):
    """AC-11: User A cannot see User B's tasks."""
    headers_a = make_auth_header(TEST_USER)
    headers_b = make_auth_header(TEST_USER_2)

    # User A creates a task
    resp = client.post("/api/v1/tasks", json={"title": "A's task"}, headers=headers_a)
    task_id = resp.json()["id"]

    # User B cannot see it
    response = client.get(f"/api/v1/tasks/{task_id}", headers=headers_b)
    assert response.status_code == 404

    # User B's list doesn't include it
    response = client.get("/api/v1/tasks", headers=headers_b)
    assert response.json()["total"] == 0


def test_data_isolation_delete(client):
    """AC-11: User B cannot delete User A's tasks."""
    headers_a = make_auth_header(TEST_USER)
    headers_b = make_auth_header(TEST_USER_2)

    resp = client.post("/api/v1/tasks", json={"title": "Protected"}, headers=headers_a)
    task_id = resp.json()["id"]

    response = client.delete(f"/api/v1/tasks/{task_id}", headers=headers_b)
    assert response.status_code == 404

    # Task still exists for User A
    response = client.get(f"/api/v1/tasks/{task_id}", headers=headers_a)
    assert response.status_code == 200
