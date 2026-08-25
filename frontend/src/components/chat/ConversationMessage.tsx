import { Bot, User, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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

      <div className="max-w-[min(640px,85%)] min-w-0 motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-1 motion-safe:duration-200">
        {/* Bubble */}
        <div
          className={`overflow-hidden rounded-xl border px-4 py-3 text-[13px] leading-relaxed shadow-sm ${
            isUser
              ? 'border-primary/20 bg-primary text-primary-foreground'
              : 'border-border bg-surface-2 text-foreground'
          }`}
        >
          {isUser ? (
            <div className="whitespace-pre-wrap break-words break-all">
              {message.content}
            </div>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none break-words prose-p:my-2 prose-headings:font-semibold prose-headings:text-foreground prose-strong:text-foreground prose-code:rounded prose-code:bg-black/30 prose-code:px-1 prose-code:py-0.5 prose-code:text-xs prose-pre:my-2 prose-pre:rounded-lg prose-pre:bg-black/40 prose-pre:p-3 prose-ul:my-2 prose-ol:my-2 prose-li:my-0.5">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
          )}

          {message.citations &&
            message.citations.length > 0 && (
              <div className="mt-3 border-t border-white/10 pt-3">
                <p className="mb-2 text-[11px] font-medium tracking-wide text-muted-foreground">
                  Sources
                </p>

                <div className="grid gap-2">
                  {message.citations.map((citation) => (
                    <div
                      key={citation.id}
                      className="flex items-start gap-2 rounded-lg border border-border bg-background/60 px-3 py-2"
                    >
                      <FileText className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                      <div className="min-w-0 flex-1">
                        <div className="truncate text-[12px] font-medium text-foreground">
                          {citation.source}
                        </div>
                        {citation.text && (
                          <div className="text-[11px] text-faint">{citation.text}</div>
                        )}
                      </div>
                      {citation.page && (
                        <span className="shrink-0 rounded bg-surface-2 px-1.5 py-0.5 text-[11px] text-muted-foreground">
                          p. {citation.page}
                        </span>
                      )}
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
