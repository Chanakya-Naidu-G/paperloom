import { ChatMessage } from "@/types/chat";

interface ConversationMessageProps {
  message: ChatMessage;
}

export function ConversationMessage({
  message,
}: ConversationMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex ${
        isUser
          ? "justify-end"
          : "justify-start"
      }`}
    >
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-zinc-900 border border-zinc-800"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}