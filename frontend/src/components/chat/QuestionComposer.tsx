'use client';

import React, { FormEvent, useState } from 'react';
import { ArrowUp } from 'lucide-react';
import { useChatStore } from '@/store/useChatStore';
import { useDocumentStore } from '@/store/useDocumentStore';
import { askQuestion } from '@/services/chatServices';
import { ChatMessage } from '@/types/chat';

export default function QuestionComposer() {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const {
    activeSessionId,
    createSession,
    addMessage,
  } = useChatStore();

  const {
    selectedDocumentId,
    getSelectedDocument,
  } = useDocumentStore();

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || isLoading) {
      return;
    }

    const document = getSelectedDocument();

    if (!document) {
      return;
    }

    setIsLoading(true);

    try {
      let sessionId = activeSessionId;

      if (!sessionId) {
        const session = createSession(document.name);
        sessionId = session.id;
      }

      const userMessage: ChatMessage = {
        id: `message-${Date.now()}`,
        role: 'user',
        content: trimmedQuestion,
        timestamp: new Date(),
      };

      addMessage(sessionId, userMessage);

      setQuestion('');

      const response = await askQuestion({
        query: trimmedQuestion,
        top_k: 5,
        document_ids: selectedDocumentId
          ? [selectedDocumentId]
          : undefined,
      });

      const assistantMessage: ChatMessage = {
        id: `message-${Date.now()}-assistant`,
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        citations: response.sources.map((source, index) => ({
          id: `${source.chunk_id}-${index}`,
          source: source.section || source.document_id,
          page: source.page_start,
          text: `Pages ${source.page_start}-${source.page_end}`,
        })),
      };

      addMessage(sessionId, assistantMessage);
    } catch (error) {
      console.error('Question failed:', error);

      let sessionId = activeSessionId;

      if (!sessionId) {
        const session = createSession(document.name);
        sessionId = session.id;
      }

      addMessage(sessionId, {
        id: `message-${Date.now()}-error`,
        role: 'assistant',
        content:
          error instanceof Error
            ? `Sorry, I couldn't answer that. ${error.message}`
            : 'Sorry, I could not answer that question.',
        timestamp: new Date(),
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-border p-4"
    >
      <div className="flex items-center gap-3 rounded-lg border border-border bg-surface-2 px-4 py-2">
        <input
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={isLoading}
          placeholder={
            isLoading
              ? 'Thinking...'
              : 'Ask anything about this paper...'
          }
          className="h-8 flex-1 bg-transparent text-[13px] text-foreground outline-none placeholder:text-faint disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={!question.trim() || isLoading}
          aria-label="Send question"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground transition-opacity hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ArrowUp className="h-4 w-4" />
        </button>
      </div>
    </form>
  );
}
