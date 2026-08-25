import { create } from 'zustand';
import { ChatSession, ChatMessage } from '@/types/chat';

interface ChatStore {
  sessions: ChatSession[];
  activeSessionId: string | null;
  
  // Session management
  createSession: (title: string, documentId: string) => ChatSession;
  deleteSession: (sessionId: string) => void;
  setActiveSession: (sessionId: string | null) => void;
  getActiveSession: () => ChatSession | null;
  getSessionForDocument: (documentId: string) => ChatSession | null;
  getOrCreateSessionForDocument: (documentId: string, title: string) => ChatSession;
  deleteSessionsForDocument: (documentId: string) => void;
  
  // Message management
  addMessage: (sessionId: string, message: ChatMessage) => void;
  updateMessage: (sessionId: string, messageId: string, content: string) => void;
  deleteMessage: (sessionId: string, messageId: string) => void;
  getSessionMessages: (sessionId: string) => ChatMessage[];
  
  // Clear
  clearChat: (sessionId: string) => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  sessions: [],
  activeSessionId: null,

  createSession: (title: string, documentId: string) => {
    const newSession: ChatSession = {
      id: `session-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      documentId,
      title,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    set((state) => ({
      sessions: [...state.sessions, newSession],
      activeSessionId: newSession.id,
    }));
    return newSession;
  },

  deleteSession: (sessionId: string) => {
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== sessionId),
      activeSessionId:
        state.activeSessionId === sessionId ? null : state.activeSessionId,
    }));
  },

  setActiveSession: (sessionId: string | null) => {
    set({ activeSessionId: sessionId });
  },

  getActiveSession: () => {
    const state = get();
    return (
      state.sessions.find((s) => s.id === state.activeSessionId) || null
    );
  },

  getSessionForDocument: (documentId: string) => {
    const state = get();
    return state.sessions.find((s) => s.documentId === documentId) || null;
  },

  getOrCreateSessionForDocument: (documentId: string, title: string) => {
    const existing = get().sessions.find((s) => s.documentId === documentId);
    if (existing) {
      if (get().activeSessionId !== existing.id) {
        set({ activeSessionId: existing.id });
      }
      return existing;
    }
    const newSession: ChatSession = {
      id: `session-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      documentId,
      title,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    set((state) => ({
      sessions: [...state.sessions, newSession],
      activeSessionId: newSession.id,
    }));
    return newSession;
  },

  deleteSessionsForDocument: (documentId: string) => {
    set((state) => {
      const remaining = state.sessions.filter((s) => s.documentId !== documentId);
      const activeStillExists = remaining.some((s) => s.id === state.activeSessionId);
      return {
        sessions: remaining,
        activeSessionId: activeStillExists ? state.activeSessionId : null,
      };
    });
  },

  addMessage: (sessionId: string, message: ChatMessage) => {
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.id === sessionId
          ? {
              ...session,
              messages: [...session.messages, message],
              updatedAt: new Date(),
            }
          : session
      ),
    }));
  },

  updateMessage: (sessionId: string, messageId: string, content: string) => {
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.id === sessionId
          ? {
              ...session,
              messages: session.messages.map((msg) =>
                msg.id === messageId ? { ...msg, content } : msg
              ),
              updatedAt: new Date(),
            }
          : session
      ),
    }));
  },

  deleteMessage: (sessionId: string, messageId: string) => {
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.id === sessionId
          ? {
              ...session,
              messages: session.messages.filter((msg) => msg.id !== messageId),
              updatedAt: new Date(),
            }
          : session
      ),
    }));
  },

  getSessionMessages: (sessionId: string) => {
    const state = get();
    return state.sessions.find((s) => s.id === sessionId)?.messages || [];
  },

  clearChat: (sessionId: string) => {
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.id === sessionId
          ? {
              ...session,
              messages: [],
              updatedAt: new Date(),
            }
          : session
      ),
    }));
  },
}));
