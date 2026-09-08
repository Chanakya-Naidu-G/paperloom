'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ResearchWorkspace from '@/components/workspace/ResearchWorkspace';
import { fetchDocuments } from '@/services/documentService';
import { useAuthStore } from '@/store/useAuthStore';
import { useChatStore } from '@/store/useChatStore';
import { useDocumentStore } from '@/store/useDocumentStore';
import { AnimatedReveal } from '@/components/ui/AnimatedReveal';
import { JumpingDots } from '@/components/ui/JumpingDots';

export default function WorkspacePage() {
  const router = useRouter();
  const token = useAuthStore((s) => s.token);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const addDocument = useDocumentStore((s) => s.addDocument);
  const clearAllDocuments = useDocumentStore((s) => s.clearAllDocuments);
  const [hydrating, setHydrating] = useState(true);
  const [hydrationError, setHydrationError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      router.replace('/login');
      return;
    }

    let cancelled = false;

    async function hydrate() {
      try {
        const items = await fetchDocuments();
        if (cancelled) return;
        // Replace local store with server truth (prevents orphaned local-only docs)
        clearAllDocuments();
        for (const item of items) {
          addDocument({
            id: item.document_id,
            name: item.original_filename,
            type: 'pdf',
            size: item.file_size,
            uploadedAt: new Date(item.uploaded_at),
            updatedAt: new Date(item.uploaded_at),
            pages: item.page_count,
            characters: item.character_count,
            chunkCount: item.chunk_count,
          });
        }
      } catch (err) {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : 'Failed to load documents.';
        if (message.includes('sign in again')) {
          useDocumentStore.getState().clearAllDocuments();
          useChatStore.setState({ sessions: [], activeSessionId: null });
          clearAuth();
          router.replace('/login');
          return;
        }
        setHydrationError(message);
      } finally {
        if (!cancelled) setHydrating(false);
      }
    }

    hydrate();
    return () => {
      cancelled = true;
    };
  }, [token, router, addDocument, clearAllDocuments, clearAuth]);

  if (!token) {
    return (
      <div className="flex h-screen items-center justify-center bg-background text-sm text-muted-foreground">
        Redirecting to sign in...
      </div>
    );
  }

  if (hydrating) {
    return (
      <div className="flex h-screen items-center justify-center gap-3 bg-background text-sm text-muted-foreground">
        <JumpingDots />
        Loading your documents...
      </div>
    );
  }

  return (
    <>
      <AnimatedReveal open={!!hydrationError}>
        <div className="border-b border-amber-500/40 bg-amber-500/10 px-4 py-2 text-center text-xs text-amber-600 dark:text-amber-400">
          {hydrationError} — your workspace is still usable.
        </div>
      </AnimatedReveal>
      <ResearchWorkspace />
    </>
  );
}
