"use client";

import { useChatStore } from "../../store/useChatStore";
import { ConversationMessage } from "./ConversationMessage";

export function ConversationHistory() {
  const messages = useChatStore(
    (state) =>
      state.sessions.find(
        (session) => session.id === state.activeSessionId
      )?.messages
  );

  if (!messages || messages.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-xs text-faint">
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
