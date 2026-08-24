'use client';

import React, { ChangeEvent, useRef, useState } from 'react';
import { FileText, Plus } from 'lucide-react';
import { uploadDocument } from '@/services/documentService';
import { useDocumentStore } from '@/store/useDocumentStore';
import { formatFileSize } from '@/lib/utils';

export default function DocumentExplorer() {
  const {
    documents,
    selectedDocumentId,
    setSelectedDocument,
    addDocument,
  } = useDocumentStore();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  async function handleFileSelect(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setError(null);
    setIsUploading(true);

    try {
      const response = await uploadDocument(file);

      if (!response.success) {
        throw new Error(response.message);
      }

      const documentId =
        response.stored_filename ?? response.original_filename ?? file.name;

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

      setSelectedDocument(documentId);
    } catch (uploadError) {
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : 'Failed to upload document.',
      );
    } finally {
      setIsUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }

  return (
    <aside className="flex h-full w-full shrink-0 flex-col bg-explorer">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Section heading */}
      <div className="flex items-center justify-between px-6 pb-4 pt-5 max-[1279px]:px-4">
        <h2 className="text-base font-semibold text-foreground">
          Documents
        </h2>

        <button
          type="button"
          onClick={openFilePicker}
          disabled={isUploading}
          aria-label="Upload document"
          className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground disabled:opacity-50"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>

      {/* Upload button: W 228 · H 40 · #2563EB · r8 */}
      <div className="px-4">
        <button
          type="button"
          onClick={openFilePicker}
          disabled={isUploading}
          className="flex h-10 max-[1023px]:h-9 w-full items-center justify-center gap-2 rounded-lg bg-primary text-[13px] font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-60"
        >
          <Plus className="h-4 w-4" />
          {isUploading ? 'Uploading...' : 'Upload PDF'}
        </button>
      </div>

      {error && (
        <div className="mx-4 mt-3 rounded-lg border border-red-500/50 bg-red-500/10 p-3 text-xs text-red-400">
          {error}
        </div>
      )}

      {/* Document cards: W 228 · H 68 · #18181B · r8 · indicator 3×68 #2563EB */}
      <div className="mt-4 flex-1 space-y-3 overflow-y-auto px-4 pb-4">
        {documents.length === 0 ? (
          <p className="px-2 text-xs text-faint">
            No documents uploaded yet
          </p>
        ) : (
          documents.map((doc) => {
            const isSelected = doc.id === selectedDocumentId;

            return (
              <button
                key={doc.id}
                type="button"
                onClick={() => setSelectedDocument(doc.id)}
                className={`relative flex h-[68px] max-[1023px]:h-[64px] w-full items-center gap-3 overflow-hidden rounded-lg border px-3 text-left transition-colors ${
                  isSelected
                    ? 'border-border bg-surface-2'
                    : 'border-border bg-surface-2/40 hover:bg-surface-2/70'
                }`}
              >
                {isSelected && (
                  <span className="absolute left-0 top-0 h-full w-[3px] rounded-[2px] bg-primary" />
                )}

                <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />

                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[13px] font-medium text-foreground">
                    {doc.name}
                  </span>

                  <span className="mt-0.5 block truncate text-[11px] text-muted-foreground">
                    {doc.pages ? `${doc.pages} pages` : 'PDF'}
                    {' · '}
                    {formatFileSize(doc.size)}
                  </span>
                </span>
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
}
