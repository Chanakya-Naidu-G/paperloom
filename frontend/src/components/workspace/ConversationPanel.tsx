'use client';

import React, { useEffect, useRef } from 'react';
import { useChatStore } from '@/store/useChatStore';
import { useDocumentStore } from '@/store/useDocumentStore';
import { ConversationHeader } from '@/components/chat/ConversationHeader';
import { ConversationHistory } from '@/components/chat/ConversationHistory';
import QuestionComposer from '@/components/chat/QuestionComposer';

export default function ConversationPanel() {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeSession = useChatStore((state) =>
    state.sessions.find(
      (session) => session.id === state.activeSessionId
    )
  );

  const selectedDocument = useDocumentStore((state) =>
    state.documents.find(
      (doc) => doc.id === state.selectedDocumentId
    )
  );

  const messageCount = activeSession?.messages.length ?? 0;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  }, [messageCount]);

  const title =
    activeSession?.title ?? selectedDocument?.name ?? 'No document selected';

  return (
    <div className="flex h-full min-w-0 flex-1 flex-col bg-conversation">
      {/* Conversation Header */}
      <ConversationHeader title={title} messageCount={messageCount} />

      {/* Conversation */}
      <div className="min-w-0 flex-1 overflow-y-auto px-6 py-6 max-[1023px]:px-4 max-[767px]:px-3">
        <ConversationHistory />

        <div ref={messagesEndRef} />
      </div>

      {/* Question Composer */}
      <QuestionComposer />
    </div>
  );
}
