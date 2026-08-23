'use client';

import React, { ChangeEvent, useRef, useState } from 'react';
import { uploadDocument } from '@/services/documentService';
import { useDocumentStore } from '@/store/useDocumentStore';

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
    <div className="flex flex-col h-full p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Documents</h2>

        <button type="button" onClick={() => alert('UPLOAD CLICKED')} className="px-3 py-1.5 rounded-md bg-red-500 text-white">UPLOAD TEST</button>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {error && (
        <div className="mb-4 rounded-md border border-red-500/50 bg-red-500/10 p-3 text-xs text-red-400">
          {error}
        </div>
      )}

      {documents.length === 0 ? (
        <div className="text-sm text-muted-foreground">
          No documents uploaded yet
        </div>
      ) : (
        <div className="space-y-2 flex-1 overflow-y-auto">
          {documents.map((doc) => (
            <button
              key={doc.id}
              onClick={() => setSelectedDocument(doc.id)}
              className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                selectedDocumentId === doc.id
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-muted'
              }`}
            >
              <div className="truncate font-medium">
                {doc.name}
              </div>

              <div className="text-xs opacity-75">
                {(doc.size / 1024 / 1024).toFixed(2)} MB
                {doc.pages && ` • ${doc.pages} pages`}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}