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
      className={`flex ${
        isUser ? 'justify-end' : 'justify-start'
      }`}
    >
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-zinc-900 border border-zinc-800'
        }`}
      >
        <div className="whitespace-pre-wrap">
          {message.content}
        </div>

        {!isUser &&
          message.citations &&
          message.citations.length > 0 && (
            <div className="mt-3 pt-3 border-t border-zinc-700">
              <p className="text-xs font-semibold mb-2 text-zinc-400">
                Sources
              </p>

              <div className="space-y-1">
                {message.citations.map((citation) => (
                  <div
                    key={citation.id}
                    className="text-xs text-zinc-400"
                  >
                    <span>{citation.source}</span>

                    {citation.page && (
                      <span className="ml-2">
                        Page {citation.page}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
      </div>
    </div>
  );
}