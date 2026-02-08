"use client";

import { Conversation } from "@/types";

interface ConversationListProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
}

function formatTime(dateStr: string | null): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onNewChat,
}: ConversationListProps) {
  return (
    <div className="flex h-full flex-col bg-gray-50 border-r border-gray-200">
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          + New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <p className="px-3 py-2 text-sm text-gray-400">No conversations yet</p>
        ) : (
          conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelect(conv.id)}
              className={`w-full px-3 py-2 text-left hover:bg-gray-100 border-b border-gray-100 ${
                activeId === conv.id ? "bg-blue-50 border-l-2 border-l-blue-600" : ""
              }`}
            >
              <p className="text-sm font-medium text-gray-900 truncate">
                {conv.title || "New conversation"}
              </p>
              <p className="text-xs text-gray-400 mt-0.5">
                {formatTime(conv.updated_at || conv.created_at)}
              </p>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
