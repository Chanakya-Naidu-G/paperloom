"use client";

import { useChatStore } from "../../store/useChatStore";
import { ConversationMessage } from "./ConversationMessage";
import { ChatMessage } from "../../types/chat";

export function ConversationHistory() {
  const messages = useChatStore((state) => {
    const activeSession = state.sessions.find(
      (session) => session.id === state.activeSessionId
    );

    return activeSession?.messages ?? [];
  });

  if (messages.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-zinc-500">
        Upload a paper and ask your first question
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <ConversationMessage
          key={message.id}
          message={message}
        />
      ))}
    </div>
  );
}