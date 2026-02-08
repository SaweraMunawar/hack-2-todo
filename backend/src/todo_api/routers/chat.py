"""Chat and conversation routes - Phase V with advanced features."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from agents import Agent, Runner, RunContextWrapper, function_tool
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from ..auth.jwt import CurrentUser, get_current_user
from ..config import settings
from ..database import get_session
from ..models import (
    ChatRequest,
    ChatResponse,
    Conversation,
    ConversationListResponse,
    Message,
    MessageListResponse,
)

router = APIRouter(prefix="/api/v1", tags=["chat"])


# --- Context for tools ---


@dataclass
class ChatContext:
    """Context passed to agent tools."""

    user_id: str


# --- Agent tools ---


@function_tool
def add_task(
    ctx: RunContextWrapper[ChatContext],
    title: str,
    description: str = "",
    priority: str = "medium",
    tags: Optional[list[str]] = None,
    due_date: Optional[str] = None,
    recurring: Optional[str] = None,
) -> str:
    """Create a new task with optional priority, tags, due date, and recurring pattern.

    Args:
        title: Task title (1-200 chars)
        description: Task description (optional, max 1000 chars)
        priority: Priority level - "high", "medium", or "low" (default: "medium")
        tags: List of tags like ["work", "urgent"] (optional)
        due_date: ISO format datetime string like "2024-01-20T18:00:00Z" (optional)
        recurring: Recurring pattern - "daily", "weekly", or "monthly" (optional)
    """
    from ..mcp.tools import add_task as _add_task

    result = _add_task(
        ctx.context.user_id,
        title,
        description,
        priority,
        tags,
        due_date,
        recurring,
    )
    return json.dumps(result)


@function_tool
def list_tasks(
    ctx: RunContextWrapper[ChatContext],
    status: str = "all",
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
) -> str:
    """View tasks with optional filters, search, and sorting.

    Args:
        status: Filter by status: "all", "pending", or "completed"
        priority: Filter by priority: "high", "medium", or "low"
        tags: Filter by tags (any matching tag)
        search: Search keyword in title
        sort_by: Sort by: "due_date", "priority", "title", or "created_at"
    """
    from ..mcp.tools import list_tasks as _list_tasks

    result = _list_tasks(
        ctx.context.user_id,
        status,
        priority,
        tags,
        search,
        sort_by,
    )
    return json.dumps(result)


@function_tool
def search_tasks(ctx: RunContextWrapper[ChatContext], query: str) -> str:
    """Search tasks by keyword in title.

    Args:
        query: Search keyword
    """
    from ..mcp.tools import search_tasks as _search_tasks

    result = _search_tasks(ctx.context.user_id, query)
    return json.dumps(result)


@function_tool
def complete_task(ctx: RunContextWrapper[ChatContext], task_id: str) -> str:
    """Mark a task as done. For recurring tasks, creates the next occurrence.

    Args:
        task_id: UUID of the task to complete
    """
    from ..mcp.tools import complete_task as _complete_task

    result = _complete_task(ctx.context.user_id, task_id)
    return json.dumps(result)


@function_tool
def delete_task(ctx: RunContextWrapper[ChatContext], task_id: str) -> str:
    """Remove a task from the list.

    Args:
        task_id: UUID of the task to delete
    """
    from ..mcp.tools import delete_task as _delete_task

    result = _delete_task(ctx.context.user_id, task_id)
    return json.dumps(result)


@function_tool
def update_task(
    ctx: RunContextWrapper[ChatContext],
    task_id: str,
    title: str = "",
    description: str = "",
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    due_date: Optional[str] = None,
    recurring: Optional[str] = None,
) -> str:
    """Update a task's properties.

    Args:
        task_id: UUID of the task to update
        title: New title (leave empty to keep current)
        description: New description (leave empty to keep current)
        priority: New priority - "high", "medium", or "low"
        tags: New tags list (replaces existing)
        due_date: New due date in ISO format
        recurring: New recurring pattern - "daily", "weekly", "monthly", or "" to clear
    """
    from ..mcp.tools import update_task as _update_task

    result = _update_task(
        ctx.context.user_id,
        task_id,
        title=title if title else None,
        description=description if description else None,
        priority=priority,
        tags=tags,
        due_date=due_date,
        recurring=recurring,
    )
    return json.dumps(result)


@function_tool
def set_priority(
    ctx: RunContextWrapper[ChatContext],
    task_id: str,
    priority: str,
) -> str:
    """Set task priority.

    Args:
        task_id: UUID of the task
        priority: Priority level - "high", "medium", or "low"
    """
    from ..mcp.tools import set_priority as _set_priority

    result = _set_priority(ctx.context.user_id, task_id, priority)
    return json.dumps(result)


@function_tool
def add_tag(
    ctx: RunContextWrapper[ChatContext],
    task_id: str,
    tag: str,
) -> str:
    """Add a tag to a task.

    Args:
        task_id: UUID of the task
        tag: Tag to add
    """
    from ..mcp.tools import add_tag as _add_tag

    result = _add_tag(ctx.context.user_id, task_id, tag)
    return json.dumps(result)


@function_tool
def remove_tag(
    ctx: RunContextWrapper[ChatContext],
    task_id: str,
    tag: str,
) -> str:
    """Remove a tag from a task.

    Args:
        task_id: UUID of the task
        tag: Tag to remove
    """
    from ..mcp.tools import remove_tag as _remove_tag

    result = _remove_tag(ctx.context.user_id, task_id, tag)
    return json.dumps(result)


@function_tool
def set_due_date(
    ctx: RunContextWrapper[ChatContext],
    task_id: str,
    due_date: str,
) -> str:
    """Set or update task due date.

    Args:
        task_id: UUID of the task
        due_date: Due date in ISO format (e.g., "2024-01-20T18:00:00Z")
    """
    from ..mcp.tools import set_due_date as _set_due_date

    result = _set_due_date(ctx.context.user_id, task_id, due_date)
    return json.dumps(result)


@function_tool
def create_recurring_task(
    ctx: RunContextWrapper[ChatContext],
    title: str,
    pattern: str,
    due_date: str,
    description: str = "",
    priority: str = "medium",
    tags: Optional[list[str]] = None,
) -> str:
    """Create a recurring task.

    Args:
        title: Task title
        pattern: Recurring pattern - "daily", "weekly", or "monthly"
        due_date: First due date in ISO format (e.g., "2024-01-20T18:00:00Z")
        description: Task description (optional)
        priority: Priority level (optional, default: "medium")
        tags: Tags list (optional)
    """
    from ..mcp.tools import create_recurring_task as _create_recurring_task

    result = _create_recurring_task(
        ctx.context.user_id,
        title,
        pattern,
        due_date,
        description,
        priority,
        tags,
    )
    return json.dumps(result)


SYSTEM_PROMPT = """You are a helpful todo list assistant with advanced task management features.
You help users manage their tasks through natural language.

Available tools:
- add_task: Create a new task with optional priority, tags, due date, and recurring pattern
- list_tasks: View tasks with filters (status, priority, tags), search, and sorting
- search_tasks: Search tasks by keyword
- complete_task: Mark a task as done (recurring tasks auto-create next occurrence)
- delete_task: Remove a task
- update_task: Change task properties (title, description, priority, tags, due date, recurring)
- set_priority: Set task priority (high, medium, low)
- add_tag: Add a tag to a task
- remove_tag: Remove a tag from a task
- set_due_date: Set or update task due date
- create_recurring_task: Create a recurring task (daily, weekly, monthly)

Rules:
1. Always confirm actions with a friendly response
2. When the user refers to a task by name but not ID, list tasks first to find the right one
3. Be concise but helpful
4. If a tool returns an error, explain it to the user
5. You can chain multiple tools in one turn if needed
6. For dates, use ISO format (e.g., "2024-01-20T18:00:00Z")
7. Priority levels are: high, medium, low
8. Recurring patterns are: daily, weekly, monthly
9. Tags can be any string like "work", "home", "urgent"
"""


def _build_agent() -> Agent[ChatContext]:
    """Build the OpenAI Agent with task tools."""
    return Agent(
        name="todo_assistant",
        instructions=SYSTEM_PROMPT,
        tools=[
            add_task,
            list_tasks,
            search_tasks,
            complete_task,
            delete_task,
            update_task,
            set_priority,
            add_tag,
            remove_tag,
            set_due_date,
            create_recurring_task,
        ],
        model=settings.OPENAI_MODEL if hasattr(settings, "OPENAI_MODEL") else "gpt-4o-mini",
    )


# --- Routes ---


@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Send a chat message and get an AI response."""
    import openai

    # Resolve or create conversation
    if data.conversation_id:
        statement = select(Conversation).where(
            Conversation.id == data.conversation_id,
            Conversation.user_id == user.id,
        )
        conversation = db.exec(statement).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=user.id, title="")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user.id,
        role="user",
        content=data.message,
    )
    db.add(user_message)
    db.commit()

    # Load conversation history for context
    history_stmt = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    history = db.exec(history_stmt).all()

    # Build input for agent: convert history to message dicts
    input_messages = []
    for msg in history:
        input_messages.append({"role": msg.role, "content": msg.content})

    # Run agent
    context = ChatContext(user_id=user.id)
    agent = _build_agent()

    try:
        result = await Runner.run(
            starting_agent=agent,
            input=input_messages,
            context=context,
        )
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {e}")

    # Extract tool calls from the run result items
    tool_calls_data = []
    for item in result.raw_responses:
        if hasattr(item, "output"):
            for output_item in item.output:
                if hasattr(output_item, "type") and output_item.type == "function_call":
                    tool_call_info = {
                        "tool": output_item.name,
                        "arguments": json.loads(output_item.arguments)
                        if isinstance(output_item.arguments, str)
                        else output_item.arguments,
                    }
                    # Try to find the tool result
                    tool_calls_data.append(tool_call_info)

    # Extract tool results from new_items
    for item in result.new_items:
        if hasattr(item, "type") and item.type == "tool_call_item":
            for tc in tool_calls_data:
                if tc["tool"] == getattr(item, "raw_item", {}).get("name", ""):
                    if not tc.get("result"):
                        tc["result"] = {}

    if result.final_output:
        response_text = str(result.final_output)
    else:
        response_text = "I couldn't process that request."

    # Auto-generate title from first message
    if not conversation.title and data.message:
        conversation.title = data.message[:100]
        db.add(conversation)

    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user.id,
        role="assistant",
        content=response_text,
        tool_calls=tool_calls_data if tool_calls_data else None,
    )
    db.add(assistant_message)

    # Update conversation timestamp
    conversation.updated_at = datetime.now(timezone.utc)
    db.add(conversation)
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text,
        tool_calls=tool_calls_data,
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """List user's conversations."""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = db.exec(statement).all()

    count_stmt = (
        select(func.count())
        .select_from(Conversation)
        .where(Conversation.user_id == user.id)
    )
    total = db.exec(count_stmt).one()

    return ConversationListResponse(conversations=conversations, total=total)


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    conversation_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get messages for a conversation."""
    # Verify conversation ownership
    conv_stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    )
    conversation = db.exec(conv_stmt).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = db.exec(msg_stmt).all()

    return MessageListResponse(messages=messages)
