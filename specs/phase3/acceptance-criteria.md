# Phase III: Acceptance Criteria

## AC-1: Chat Endpoint
- [ ] POST /api/v1/chat accepts message and optional conversation_id
- [ ] Returns AI response with conversation_id and tool_calls
- [ ] Creates new conversation when conversation_id is null
- [ ] Resumes existing conversation when conversation_id is provided
- [ ] Returns 401 for unauthenticated requests
- [ ] Returns 404 for conversation not owned by user

## AC-2: MCP Tools - add_task
- [ ] "Add a task to buy groceries" creates a task with title "Buy groceries"
- [ ] "I need to remember to pay bills" creates task "Pay bills"
- [ ] Task is created for the authenticated user
- [ ] Response confirms task creation with title

## AC-3: MCP Tools - list_tasks
- [ ] "Show me all my tasks" returns all user tasks
- [ ] "What's pending?" returns only incomplete tasks
- [ ] "What have I completed?" returns only completed tasks
- [ ] Empty list returns friendly message

## AC-4: MCP Tools - complete_task
- [ ] "Mark task X as complete" toggles task completion
- [ ] Response confirms which task was completed
- [ ] Returns error for non-existent task

## AC-5: MCP Tools - delete_task
- [ ] "Delete task X" removes the task
- [ ] Response confirms deletion with task title
- [ ] Returns error for non-existent task

## AC-6: MCP Tools - update_task
- [ ] "Change task X to 'new title'" updates task title
- [ ] Response confirms update
- [ ] Returns error for non-existent task

## AC-7: Conversation Persistence
- [ ] Messages stored in database
- [ ] Conversation history loaded on resume
- [ ] Agent has context from previous messages
- [ ] Conversations survive server restart

## AC-8: Data Isolation
- [ ] User A cannot access User B's conversations
- [ ] Chat tools only operate on authenticated user's tasks
- [ ] 404 returned for cross-user conversation access

## AC-9: Frontend Chat UI
- [ ] Chat page accessible at /chat
- [ ] Protected route (redirects to login)
- [ ] Conversation list in sidebar
- [ ] Message display with user/assistant distinction
- [ ] Text input with send functionality
- [ ] Loading indicator during AI processing
- [ ] New chat button creates fresh conversation

## AC-10: Error Handling
- [ ] AI processing failures return user-friendly error
- [ ] Network errors handled gracefully
- [ ] Tool execution errors reported in chat
- [ ] Invalid conversation_id returns 404

## AC-11: Agent Behavior
- [ ] Agent chains tools when needed (list then delete)
- [ ] Agent confirms actions with friendly responses
- [ ] Agent handles ambiguous references
- [ ] Agent provides helpful responses for non-task queries

## Test Scenarios

### TS-1: Happy Path - New Conversation
1. User opens /chat
2. Types "Add a task to buy groceries"
3. Receives confirmation with task title
4. Types "Show me my tasks"
5. Receives list including "Buy groceries"
6. Types "Mark it as complete"
7. Receives completion confirmation

### TS-2: Conversation Resume
1. User has existing conversation with messages
2. User navigates away and returns
3. Previous messages are displayed
4. New message has full context from history

### TS-3: Multi-Tool Chaining
1. User types "Delete the groceries task"
2. Agent calls list_tasks to find matching task
3. Agent calls delete_task with found task_id
4. User receives confirmation of deletion

### TS-4: Error Handling
1. User tries to complete non-existent task
2. Agent reports task not found
3. User tries to access another user's conversation
4. Receives 404 error
