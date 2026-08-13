import { create } from 'zustand';
import { ChatSession, ChatMessage } from '@/types/chat';

interface ChatStore {
  sessions: ChatSession[];
  activeSessionId: string | null;
  
  // Session management
  createSession: (title: string) => ChatSession;
  deleteSession: (sessionId: string) => void;
  setActiveSession: (sessionId: string) => void;
  getActiveSession: () => ChatSession | null;
  
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

  createSession: (title: string) => {
    const newSession: ChatSession = {
      id: `session-${Date.now()}`,
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

  setActiveSession: (sessionId: string) => {
    set({ activeSessionId: sessionId });
  },

  getActiveSession: () => {
    const state = get();
    return (
      state.sessions.find((s) => s.id === state.activeSessionId) || null
    );
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
