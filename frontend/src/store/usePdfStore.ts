import { create } from 'zustand';

export interface PDFPage {
  pageNumber: number;
  content: string;
  imageUrl?: string;
}

export interface PDFDocument {
  id: string;
  name: string;
  pages: PDFPage[];
  totalPages: number;
  uploadedAt: Date;
}

interface PDFStore {
  pdfs: PDFDocument[];
  currentPdfId: string | null;
  currentPageNumber: number;
  
  // PDF management
  addPDF: (pdf: PDFDocument) => void;
  deletePDF: (pdfId: string) => void;
  getPDF: (pdfId: string) => PDFDocument | null;
  getAllPDFs: () => PDFDocument[];
  
  // Current PDF
  setCurrentPDF: (pdfId: string) => void;
  getCurrentPDF: () => PDFDocument | null;
  
  // Pagination
  setCurrentPage: (pageNumber: number) => void;
  getCurrentPage: () => PDFPage | null;
  nextPage: () => void;
  previousPage: () => void;
  
  // Clear
  clearAllPDFs: () => void;
}

export const usePdfStore = create<PDFStore>((set, get) => ({
  pdfs: [],
  currentPdfId: null,
  currentPageNumber: 1,

  addPDF: (pdf: PDFDocument) => {
    set((state) => ({
      pdfs: [...state.pdfs, pdf],
      currentPdfId: state.currentPdfId || pdf.id,
    }));
  },

  deletePDF: (pdfId: string) => {
    set((state) => ({
      pdfs: state.pdfs.filter((pdf) => pdf.id !== pdfId),
      currentPdfId: state.currentPdfId === pdfId ? null : state.currentPdfId,
      currentPageNumber: 1,
    }));
  },

  getPDF: (pdfId: string) => {
    const state = get();
    return state.pdfs.find((pdf) => pdf.id === pdfId) || null;
  },

  getAllPDFs: () => {
    return get().pdfs;
  },

  setCurrentPDF: (pdfId: string) => {
    set({
      currentPdfId: pdfId,
      currentPageNumber: 1,
    });
  },

  getCurrentPDF: () => {
    const state = get();
    return state.pdfs.find((pdf) => pdf.id === state.currentPdfId) || null;
  },

  setCurrentPage: (pageNumber: number) => {
    const state = get();
    const pdf = state.pdfs.find((p) => p.id === state.currentPdfId);
    if (pdf && pageNumber >= 1 && pageNumber <= pdf.totalPages) {
      set({ currentPageNumber: pageNumber });
    }
  },

  getCurrentPage: () => {
    const state = get();
    const pdf = state.pdfs.find((p) => p.id === state.currentPdfId);
    if (!pdf) return null;
    return pdf.pages.find((page) => page.pageNumber === state.currentPageNumber) || null;
  },

  nextPage: () => {
    const state = get();
    const pdf = state.pdfs.find((p) => p.id === state.currentPdfId);
    if (pdf && state.currentPageNumber < pdf.totalPages) {
      set({ currentPageNumber: state.currentPageNumber + 1 });
    }
  },

  previousPage: () => {
    const state = get();
    if (state.currentPageNumber > 1) {
      set({ currentPageNumber: state.currentPageNumber - 1 });
    }
  },

  clearAllPDFs: () => {
    set({
      pdfs: [],
      currentPdfId: null,
      currentPageNumber: 1,
    });
  },
}));
