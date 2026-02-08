// Phase V: Priority type
export type Priority = "high" | "medium" | "low";

// Phase V: Recurring pattern type
export type RecurringPattern = "daily" | "weekly" | "monthly";

export interface Task {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string | null;
  // Phase V fields
  priority: Priority;
  tags: string[];
  due_date: string | null;
  recurring: RecurringPattern | null;
  recurring_parent_id: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  // Phase V fields
  priority?: Priority;
  tags?: string[];
  due_date?: string;
  recurring?: RecurringPattern;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
  // Phase V fields
  priority?: Priority;
  tags?: string[];
  due_date?: string | null;
  recurring?: RecurringPattern | null;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  pending_count: number;
  completed_count: number;
}

// Phase V: Task filter params
export interface TaskFilterParams {
  status?: "all" | "pending" | "completed";
  priority?: Priority;
  tags?: string;
  search?: string;
  sort?: "due_date" | "priority" | "title" | "created_at";
  order?: "asc" | "desc";
  limit?: number;
  offset?: number;
}

// Phase III: Chat types

export interface ToolCall {
  tool: string;
  arguments: Record<string, unknown>;
  result?: Record<string, unknown>;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCall[];
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  tool_calls: ToolCall[] | null;
  created_at: string;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
}

export interface MessageListResponse {
  messages: ChatMessage[];
}
