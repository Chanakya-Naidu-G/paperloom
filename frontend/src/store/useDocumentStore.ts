import { create } from 'zustand';
import { Document } from '@/types/document';
import { useChatStore } from '@/store/useChatStore';

interface DocumentStore {
  documents: Document[];
  selectedDocumentId: string | null;
  
  // Document management
  addDocument: (document: Document) => void;
  deleteDocument: (documentId: string) => void;
  updateDocument: (documentId: string, document: Partial<Document>) => void;
  getDocument: (documentId: string) => Document | null;
  getAllDocuments: () => Document[];
  
  // Selection
  setSelectedDocument: (documentId: string | null) => void;
  getSelectedDocument: () => Document | null;
  
  // Search
  searchDocuments: (query: string) => Document[];
  
  // Clear
  clearAllDocuments: () => void;
}

export const useDocumentStore = create<DocumentStore>((set, get) => ({
  documents: [],
  selectedDocumentId: null,

  addDocument: (document: Document) => {
    set((state) => {
      const existingIndex = state.documents.findIndex(
        (d) => d.id === document.id,
      );
      if (existingIndex !== -1) {
        const next = [...state.documents];
        next[existingIndex] = { ...next[existingIndex], ...document, updatedAt: new Date() };
        return { documents: next };
      }
      return { documents: [...state.documents, document] };
    });
  },

  deleteDocument: (documentId: string) => {
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== documentId),
      selectedDocumentId:
        state.selectedDocumentId === documentId ? null : state.selectedDocumentId,
    }));
    // Also remove the document's chat session to avoid orphaned sessions
    try {
      useChatStore.getState().deleteSessionsForDocument(documentId);
    } catch {}
  },

  updateDocument: (documentId: string, updates: Partial<Document>) => {
    set((state) => ({
      documents: state.documents.map((doc) =>
        doc.id === documentId
          ? { ...doc, ...updates, updatedAt: new Date() }
          : doc
      ),
    }));
  },

  getDocument: (documentId: string) => {
    const state = get();
    return state.documents.find((doc) => doc.id === documentId) || null;
  },

  getAllDocuments: () => {
    return get().documents;
  },

  setSelectedDocument: (documentId: string | null) => {
    set({ selectedDocumentId: documentId });
  },

  getSelectedDocument: () => {
    const state = get();
    return (
      state.documents.find((doc) => doc.id === state.selectedDocumentId) || null
    );
  },

  searchDocuments: (query: string) => {
    const state = get();
    const lowerQuery = query.toLowerCase();

    return state.documents.filter((doc) =>
      doc.name.toLowerCase().includes(lowerQuery)
    );
  },

  clearAllDocuments: () => {
    set({
      documents: [],
      selectedDocumentId: null,
    });
  },
}));
