import { create } from 'zustand';
import { Document } from '@/types/document';

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
    set((state) => ({
      documents: [...state.documents, document],
    }));
  },

  deleteDocument: (documentId: string) => {
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== documentId),
      selectedDocumentId:
        state.selectedDocumentId === documentId ? null : state.selectedDocumentId,
    }));
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
