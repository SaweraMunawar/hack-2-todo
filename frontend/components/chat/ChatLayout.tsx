"use client";

import { useState, useEffect, useCallback } from "react";
import { ChatMessage, Conversation } from "@/types";
import { sendChatMessage, getConversations, getMessages } from "@/lib/api";
import { ConversationList } from "./ConversationList";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";

export function ChatLayout() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data.conversations);
    } catch {
      // Silently handle - user may not have any conversations yet
    }
  };

  const loadMessages = useCallback(async (conversationId: string) => {
    try {
      const data = await getMessages(conversationId);
      setMessages(data.messages);
    } catch {
      setMessages([]);
    }
  }, []);

  const handleSelectConversation = useCallback(
    (id: string) => {
      setActiveConversationId(id);
      loadMessages(id);
    },
    [loadMessages]
  );

  const handleNewChat = useCallback(() => {
    setActiveConversationId(null);
    setMessages([]);
  }, []);

  const handleSend = useCallback(
    async (message: string) => {
      // Optimistically add user message
      const tempUserMsg: ChatMessage = {
        id: "temp-" + Date.now(),
        role: "user",
        content: message,
        tool_calls: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempUserMsg]);
      setLoading(true);

      try {
        const response = await sendChatMessage({
          conversation_id: activeConversationId || undefined,
          message,
        });

        // If this was a new conversation, set the active ID
        if (!activeConversationId) {
          setActiveConversationId(response.conversation_id);
        }

        // Add assistant message
        const assistantMsg: ChatMessage = {
          id: "resp-" + Date.now(),
          role: "assistant",
          content: response.response,
          tool_calls: response.tool_calls.length > 0 ? response.tool_calls : null,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);

        // Refresh conversation list
        await loadConversations();
      } catch (err) {
        // Add error message
        const errorMsg: ChatMessage = {
          id: "err-" + Date.now(),
          role: "assistant",
          content:
            err instanceof Error
              ? `Sorry, something went wrong: ${err.message}`
              : "Sorry, something went wrong. Please try again.",
          tool_calls: null,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      } finally {
        setLoading(false);
      }
    },
    [activeConversationId, loadConversations]
  );

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Mobile sidebar toggle */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="fixed bottom-4 left-4 z-10 rounded-full bg-blue-600 p-2 text-white shadow-lg md:hidden"
      >
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d={sidebarOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
          />
        </svg>
      </button>

      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "w-64" : "w-0"
        } flex-shrink-0 overflow-hidden transition-all duration-200 md:w-64`}
      >
        <ConversationList
          conversations={conversations}
          activeId={activeConversationId}
          onSelect={handleSelectConversation}
          onNewChat={handleNewChat}
        />
      </div>

      {/* Chat area */}
      <div className="flex flex-1 flex-col">
        <ChatMessages messages={messages} loading={loading} />
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>
    </div>
  );
}
