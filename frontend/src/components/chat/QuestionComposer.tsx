'use client';

import { FormEvent, useState } from 'react';
import { askQuestion } from '@/services/chatServices';
import { useChatStore } from '@/store/useChatStore';
import { Citation } from '@/types/chat';

export function QuestionComposer() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const {
    sessions,
    activeSessionId,
    createSession,
    addMessage,
  } = useChatStore();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery || isLoading) {
      return;
    }

    let sessionId = activeSessionId;

    if (!sessionId) {
      const session = createSession(trimmedQuery.slice(0, 40));
      sessionId = session.id;
    }

    addMessage(sessionId, {
      id: `message-${Date.now()}`,
      role: 'user',
      content: trimmedQuery,
      timestamp: new Date(),
    });

    setQuery('');
    setIsLoading(true);

    try {
      const response = await askQuestion(trimmedQuery);

      const citations: Citation[] = response.sources.map((source) => ({
        id: source.chunk_id,
        source: source.section,
        page:
          source.page_start === source.page_end
            ? source.page_start
            : undefined,
        text: `Pages ${source.page_start}-${source.page_end}`,
      }));

      addMessage(sessionId, {
        id: `message-${Date.now()}-assistant`,
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        citations,
      });
    } catch (error) {
      addMessage(sessionId, {
        id: `message-${Date.now()}-error`,
        role: 'assistant',
        content:
          error instanceof Error
            ? `Unable to get an answer: ${error.message}`
            : 'Unable to get an answer. Please try again.',
        timestamp: new Date(),
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex gap-2"
    >
      <input
        type="text"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Ask a question about your documents..."
        disabled={isLoading}
        className="flex-1 px-3 py-2 rounded-md border-2 border-border bg-background text-sm outline-none focus:ring-2 focus:ring-primary"
      />

      <button
        type="submit"
        disabled={isLoading || !query.trim()}
        className="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Thinking...' : 'Send'}
      </button>
    </form>
  );
}