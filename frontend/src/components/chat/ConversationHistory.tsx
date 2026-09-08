"use client";

import { useRef, useState } from "react";
import { motion } from "motion/react";
import { FileText, Upload } from "lucide-react";
import { useRouter } from "next/navigation";
import { useChatStore } from "../../store/useChatStore";
import { useDocumentStore } from "../../store/useDocumentStore";
import { useAuthStore } from "../../store/useAuthStore";
import { uploadDocument } from "@/services/documentService";
import { ConversationMessage } from "./ConversationMessage";
import { AnimatedReveal } from "@/components/ui/AnimatedReveal";
import { JumpingDots } from "@/components/ui/JumpingDots";

export function ConversationHistory() {
  const router = useRouter();
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const documents = useDocumentStore((s) => s.documents);
  const selectedDocumentId = useDocumentStore((s) => s.selectedDocumentId);
  const selectedDocument = useDocumentStore((s) =>
    s.documents.find((doc) => doc.id === s.selectedDocumentId),
  );
  const messages = useChatStore(
    (state) =>
      state.sessions.find(
        (session) => session.id === state.activeSessionId
      )?.messages
  );

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  async function handleFileSelect(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setError(null);
    setIsUploading(true);
    try {
      const response = await uploadDocument(file);
      if (!response.success) throw new Error(response.message);
      const documentId = response.document_id ?? response.original_filename ?? file.name;
      const { addDocument } = useDocumentStore.getState();
      addDocument({
        id: documentId,
        name: response.original_filename ?? file.name,
        type: 'pdf',
        size: file.size,
        uploadedAt: new Date(),
        updatedAt: new Date(),
        pages: response.pages,
        characters: response.characters,
        chunkCount: response.chunk_count,
      });
      const chatState = (await import("../../store/useChatStore")).useChatStore.getState();
      const existing = chatState.getSessionForDocument(documentId);
      useDocumentStore.getState().setSelectedDocument(documentId);
      if (existing) chatState.setActiveSession(existing.id);
      else chatState.setActiveSession(null);
    } catch (uploadError) {
      const message = uploadError instanceof Error ? uploadError.message : 'Failed to upload document.';
      if (message.includes('sign in again')) {
        useDocumentStore.getState().clearAllDocuments();
        const { useChatStore } = await import("../../store/useChatStore");
        useChatStore.setState({ sessions: [], activeSessionId: null });
        clearAuth();
        router.replace('/login');
        return;
      }
      setError(message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }

  if (!messages || messages.length === 0) {
    // No documents at all — branded welcome + prominent upload
    if (documents.length === 0) {
      return (
        <div className="flex h-full items-center justify-center p-6">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileSelect}
            className="hidden"
          />
          <div className="flex w-full max-w-md flex-col items-center rounded-2xl border border-border bg-surface p-8 text-center shadow-sm max-[767px]:p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-sm">
              <FileText className="h-6 w-6" />
            </div>
            <h2 className="mt-4 text-lg font-semibold tracking-tight text-foreground">Welcome to PaperLoom</h2>
            <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground">
              Your intelligent research companion. Upload a PDF to start a private, grounded conversation with your documents.
            </p>
            <motion.button
              type="button"
              onClick={openFilePicker}
              disabled={isUploading}
              whileTap={isUploading ? undefined : { scale: 0.97 }}
              className="mt-6 inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-primary px-6 text-sm font-medium text-primary-foreground shadow-sm transition hover:bg-primary/90 disabled:opacity-60 motion-safe:transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
            >
              {isUploading ? (
                <>
                  <JumpingDots />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Upload your first PDF
                </>
              )}
            </motion.button>
            <AnimatedReveal open={!!error} className="mt-4 w-full">
              <div className="w-full rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-400">
                {error}
              </div>
            </AnimatedReveal>
            <p className="mt-4 text-xs text-faint">PDF only • 50MB max • Per-user isolated</p>
          </div>
        </div>
      );
    }

    // Documents exist but none selected
    if (!selectedDocumentId || !selectedDocument) {
      return (
        <div className="flex h-full items-center justify-center p-6">
          <div className="flex w-full max-w-md flex-col items-center rounded-2xl border border-dashed border-border bg-surface/50 p-8 text-center max-[767px]:p-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-surface-2 text-muted-foreground">
              <FileText className="h-5 w-5" />
            </div>
            <h3 className="mt-4 text-sm font-semibold text-foreground">No document selected</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              Select a document from the sidebar to view its conversation, or upload a new PDF to begin.
            </p>
          </div>
        </div>
      );
    }

    // Document selected but no messages yet
    return (
      <div className="flex h-full items-center justify-center p-6">
        <div className="flex w-full max-w-md flex-col items-center rounded-2xl border border-border bg-surface p-6 text-center">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <FileText className="h-5 w-5" />
          </div>
          <h3 className="mt-3 text-sm font-semibold text-foreground">{selectedDocument.name}</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            {selectedDocument.pages ? `${selectedDocument.pages} pages` : 'PDF'} • Ask your first question to start
          </p>
          <p className="mt-4 text-sm text-faint">Try “Summarize this paper” from the Context panel.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <ConversationMessage
          key={message.id}
          message={message}
        />
      ))}
    </div>
  );
}
