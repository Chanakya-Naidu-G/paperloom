'use client';

import React, { useRef } from 'react';
import { useChatStore } from '@/store/useChatStore';
import { ConversationMessage } from '@/components/chat/ConversationMessage';
import { QuestionComposer } from '@/components/chat/QuestionComposer';

export default function ConversationPanel() {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeSession = useChatStore((state) =>
    state.sessions.find(
      (session) => session.id === state.activeSessionId
    )
  );

  const messages = activeSession?.messages ?? [];

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-background rounded-lg border-2 border-border">
      <div className="border-b-2 border-border p-4">
        <h2 className="text-lg font-semibold">
          {activeSession?.title || 'PaperLoom'}
        </h2>

        <p className="text-sm text-muted-foreground">
          {messages.length} messages
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            Upload a paper and ask your first question
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <ConversationMessage
                key={message.id}
                message={message}
              />
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t-2 border-border p-4">
        <QuestionComposer />
      </div>
    </div>
  );
}