'use client';

/* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */

import React, { useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, Loader2, X } from 'lucide-react';
import { useDocumentStore } from '@/store/useDocumentStore';
import { API_BASE_URL, getAuthHeaders } from '@/lib/api';

interface DocumentViewerPanelProps {
  onClose?: () => void;
}

export default function DocumentViewerPanel({ onClose }: DocumentViewerPanelProps) {
  const selectedDoc = useDocumentStore((s) =>
    s.documents.find((doc) => doc.id === s.selectedDocumentId),
  );

  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = selectedDoc?.pages ?? 0;

  // Reset page when document changes (intentional sync reset)
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedDoc?.id]);

  useEffect(() => {
    if (!selectedDoc) {
      setBlobUrl(null);
      setError(null);
      return;
    }

    let cancelled = false;
    let objectUrl: string | null = null;

    async function loadPdf() {
      setLoading(true);
      setError(null);
      setBlobUrl(null);
      try {
        const headers = getAuthHeaders();
        const res = await fetch(
          `${API_BASE_URL}/documents/${selectedDoc!.id}/pdf`,
          { headers },
        );
        if (!res.ok) {
          let msg = 'Failed to load PDF.';
          try {
            const data = await res.json();
            if (typeof data?.detail === 'string') msg = data.detail;
          } catch {}
          throw new Error(msg);
        }
        const blob = await res.blob();
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setBlobUrl(objectUrl);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Failed to load PDF.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadPdf();

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [selectedDoc?.id]);

  // Clean up blob on unmount
  useEffect(() => {
    return () => {
      if (blobUrl) URL.revokeObjectURL(blobUrl);
    };
  }, [blobUrl]);

  const canPrev = currentPage > 1;
  const canNext = totalPages ? currentPage < totalPages : true;

  const handlePrev = () => {
    if (canPrev) setCurrentPage((p) => Math.max(1, p - 1));
  };
  const handleNext = () => {
    if (canNext) setCurrentPage((p) => (totalPages ? Math.min(totalPages, p + 1) : p + 1));
  };

  // Build iframe src with page fragment so browser viewer jumps to page
  const iframeSrc = blobUrl ? `${blobUrl}#page=${currentPage}&toolbar=0&navpanes=0` : null;

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-border bg-viewer">
      {/* Header: filename left, page count center/right, close independent */}
      <div className="flex h-12 shrink-0 items-center gap-3 border-b border-border bg-surface px-4">
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-sm font-semibold text-foreground">
            {selectedDoc?.name || 'Document Viewer'}
          </h2>
        </div>

        {selectedDoc && (
          <span className="shrink-0 whitespace-nowrap text-xs text-muted-foreground">
            {totalPages ? `${totalPages} pages` : 'PDF'}
          </span>
        )}

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close viewer"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Viewer content */}
      <div className="flex min-h-0 flex-1 flex-col bg-background">
        {!selectedDoc ? (
          <div className="flex flex-1 items-center justify-center p-6 text-center text-sm text-muted-foreground">
            Select a document to view
          </div>
        ) : loading ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-3 p-6 text-sm text-muted-foreground">
            <Loader2 className="h-6 w-6 animate-spin" />
            Loading PDF...
          </div>
        ) : error ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-2 p-6 text-center">
            <p className="text-sm text-red-400">{error}</p>
            <p className="text-xs text-muted-foreground">Try selecting the document again.</p>
          </div>
        ) : iframeSrc ? (
          <iframe
            key={`${selectedDoc.id}-${blobUrl}`}
            src={iframeSrc}
            title={selectedDoc.name}
            className="h-full w-full border-0 bg-white"
          />
        ) : (
          <div className="flex flex-1 items-center justify-center p-6 text-sm text-muted-foreground">
            PDF preview will appear here.
          </div>
        )}
      </div>

      {/* Footer: Previous / 1 / 30 / Next — always visible when doc selected */}
      {selectedDoc && (
        <div className="flex h-12 shrink-0 items-center justify-between border-t border-border bg-surface px-4">
          <button
            type="button"
            onClick={handlePrev}
            disabled={!canPrev || loading || !!error || !blobUrl}
            className="inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium text-foreground transition hover:bg-surface-2 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </button>

          <span className="text-sm tabular-nums text-muted-foreground">
            {currentPage} / {totalPages || '?'}
          </span>

          <button
            type="button"
            onClick={handleNext}
            disabled={!canNext || loading || !!error || !blobUrl}
            className="inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium text-foreground transition hover:bg-surface-2 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
