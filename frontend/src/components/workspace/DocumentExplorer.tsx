'use client';

import React from 'react';
import { useDocumentStore } from '@/store/useDocumentStore';

export default function DocumentExplorer() {
  const { documents, selectedDocumentId, setSelectedDocument } =
    useDocumentStore();

  return (
    <div className="flex flex-col h-full p-4">
      <h2 className="text-lg font-semibold mb-4">Documents</h2>

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
              <div className="truncate font-medium">{doc.name}</div>
              <div className="text-xs opacity-75">
                {(doc.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
