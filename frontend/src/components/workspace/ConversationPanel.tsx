'use client';

import React, { useRef } from 'react';
import { useChatStore } from '@/store/useChatStore';

export default function ConversationPanel() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { getActiveSession, getSessionMessages } = useChatStore();

  const activeSession = getActiveSession();
  const messages = React.useMemo(
    () => (activeSession ? getSessionMessages(activeSession.id) : []),
    [activeSession, getSessionMessages]
  );

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-background rounded-lg border-2 border-border">
      {/* Header */}
      <div className="border-b-2 border-border p-4">
        <h2 className="text-lg font-semibold">
          {activeSession?.title || 'No active session'}
        </h2>
        <p className="text-sm text-muted-foreground">
          {messages.length} messages
        </p>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            No messages yet. Start a conversation!
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-xs px-4 py-2 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-foreground'
                }`}
              >
                <p className="text-sm">{msg.content}</p>
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-current/20 text-xs opacity-75">
                    <p className="font-semibold">Citations:</p>
                    {msg.citations.map((cite) => (
                      <p key={cite.id}>{cite.source}</p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t-2 border-border p-4">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Type your message..."
            className="flex-1 px-3 py-2 rounded-md border-2 border-border bg-background text-sm"
          />
          <button className="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
