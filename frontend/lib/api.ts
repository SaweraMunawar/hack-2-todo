import { authClient } from "./auth-client";
import {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskListResponse,
  TaskFilterParams,
  ChatResponse,
  ConversationListResponse,
  MessageListResponse,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const result = await authClient.token();
  const data = result.data;
  const token = data?.token;

  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    window.location.href = "/login";
    throw new Error("Session expired");
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Request failed");
  }

  return response;
}

export async function getTasks(
  params?: TaskFilterParams
): Promise<TaskListResponse> {
  const searchParams = new URLSearchParams();

  // Status filter
  if (params?.status) {
    searchParams.set("status", params.status);
  }

  // Priority filter
  if (params?.priority) {
    searchParams.set("priority", params.priority);
  }

  // Tags filter (comma-separated)
  if (params?.tags) {
    searchParams.set("tags", params.tags);
  }

  // Search
  if (params?.search) {
    searchParams.set("search", params.search);
  }

  // Sorting
  if (params?.sort) {
    searchParams.set("sort", params.sort);
  }
  if (params?.order) {
    searchParams.set("order", params.order);
  }

  // Pagination
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));

  const query = searchParams.toString();
  const response = await fetchWithAuth(`/tasks${query ? `?${query}` : ""}`);
  return response.json();
}

export async function createTask(data: TaskCreate): Promise<Task> {
  const response = await fetchWithAuth("/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function updateTask(id: string, data: TaskUpdate): Promise<Task> {
  const response = await fetchWithAuth(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function deleteTask(id: string): Promise<void> {
  await fetchWithAuth(`/tasks/${id}`, { method: "DELETE" });
}

export async function toggleTask(id: string): Promise<Task> {
  const response = await fetchWithAuth(`/tasks/${id}/toggle`, {
    method: "POST",
  });
  return response.json();
}

// Phase III: Chat API functions

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

export async function getConversations(): Promise<ConversationListResponse> {
  const response = await fetchWithAuth("/conversations");
  return response.json();
}

export async function getMessages(
  conversationId: string
): Promise<MessageListResponse> {
  const response = await fetchWithAuth(
    `/conversations/${conversationId}/messages`
  );
  return response.json();
}
