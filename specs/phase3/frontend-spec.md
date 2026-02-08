# Phase III: Frontend Specification

## Overview
Phase III adds a ChatKit-based chat interface to the existing Phase II frontend. The existing task management UI remains available.

## Technology
- OpenAI ChatKit for chat UI
- Next.js App Router
- Better Auth (existing)

## New Routes

### /chat - Chat Interface
**Auth Required**: Yes (redirect to /login if not authenticated)

**Layout**:
```
+------------------------------------------+
| Header (Todo App | user@email | Logout)  |
+------------------------------------------+
| Sidebar        | Chat Area              |
| Conversations  | +--------------------+ |
| - Conv 1       | | Messages           | |
| - Conv 2       | | [user]: Add task.. | |
| - New Chat     | | [bot]: Done! I've  | |
|                | |  added...          | |
|                | +--------------------+ |
|                | [Type a message...  ] |  |
+------------------------------------------+
```

## Components

### ChatPage (app/chat/page.tsx)
- Server component for auth check
- Redirects to /login if not authenticated
- Renders ChatLayout

### ChatLayout (components/chat/ChatLayout.tsx)
- Client component
- Manages conversation list and active conversation
- Sidebar + main chat area

### ConversationList (components/chat/ConversationList.tsx)
- Lists user's conversations
- "New Chat" button
- Click to switch conversation
- Shows conversation title and last update time

### ChatMessages (components/chat/ChatMessages.tsx)
- Displays messages for active conversation
- Scrolls to bottom on new messages
- Shows user messages on right, assistant on left
- Shows tool call indicators (e.g., "Added task: Buy groceries")

### ChatInput (components/chat/ChatInput.tsx)
- Text input with send button
- Enter to send, Shift+Enter for newline
- Disabled while waiting for response
- Shows loading indicator during AI processing

## API Client Extensions (lib/api.ts)

```typescript
// Send chat message
export async function sendChatMessage(data: {
  conversation_id?: string;
  message: string;
}): Promise<ChatResponse> {
  const response = await fetchWithAuth("/chat", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return response.json();
}

// List conversations
export async function getConversations(): Promise<ConversationListResponse> {
  const response = await fetchWithAuth("/conversations");
  return response.json();
}

// Get conversation messages
export async function getMessages(conversationId: string): Promise<MessageListResponse> {
  const response = await fetchWithAuth(`/conversations/${conversationId}/messages`);
  return response.json();
}
```

## TypeScript Types

```typescript
interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCall[];
}

interface ToolCall {
  tool: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string | null;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  tool_calls: ToolCall[] | null;
  created_at: string;
}

interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
}

interface MessageListResponse {
  messages: ChatMessage[];
}
```

## Navigation Updates
- Header: Add "Chat" link next to "Tasks"
- Home page: Add option to go to /chat

## Environment Variables (new)
```
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here  # For hosted ChatKit
```

## Styling
- Chat messages: Rounded bubbles with user (blue, right-aligned) and assistant (gray, left-aligned)
- Tool call indicators: Small pill-shaped badges showing tool name
- Conversation list: Clean list with hover effects
- Responsive: Stack sidebar above chat on mobile
