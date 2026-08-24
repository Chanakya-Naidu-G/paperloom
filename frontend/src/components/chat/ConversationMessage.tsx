import { Bot, User } from 'lucide-react';
import { ChatMessage } from '@/types/chat';

interface ConversationMessageProps {
  message: ChatMessage;
}

export function ConversationMessage({
  message,
}: ConversationMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex gap-3 ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      {/* Avatar */}
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-border bg-surface-2">
        {isUser ? (
          <User className="h-4 w-4 text-foreground" />
        ) : (
          <Bot className="h-4 w-4 text-muted-foreground" />
        )}
      </div>

      <div className="max-w-[480px] min-w-0">
        {/* Bubble */}
        <div
          className={`rounded-xl border px-4 py-3 text-[13px] leading-relaxed ${
            isUser
              ? 'border-blue-900/40 bg-[#182A4A] text-foreground'
              : 'border-border bg-surface-2 text-foreground'
          }`}
        >
          <div className="whitespace-pre-wrap break-words">
            {message.content}
          </div>

          {message.citations &&
            message.citations.length > 0 && (
              <div className="mt-3 border-t border-white/10 pt-2">
                <p className="mb-1 text-[11px] font-medium text-muted-foreground">
                  Sources
                </p>

                <div className="space-y-1">
                  {message.citations.map((citation) => (
                    <div
                      key={citation.id}
                      className="break-words text-[11px] text-faint"
                    >
                      {citation.source}
                      {citation.page &&
                        ` · Page ${citation.page}`}
                    </div>
                  ))}
                </div>
              </div>
            )}
        </div>

        {/* Timestamp */}
        <div
          className={`mt-1 text-[11px] text-faint ${
            isUser ? 'text-right' : 'text-left'
          }`}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: 'numeric',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
}
