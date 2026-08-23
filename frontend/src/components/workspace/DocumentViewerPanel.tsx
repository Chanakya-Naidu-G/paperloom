'use client';

import React from 'react';
import Image from 'next/image';
import { useDocumentStore } from '@/store/useDocumentStore';
import { usePdfStore } from '@/store/usePdfStore';

export default function DocumentViewerPanel() {
  const { getSelectedDocument } = useDocumentStore();
  const { getCurrentPDF, getCurrentPage, nextPage, previousPage } =
    usePdfStore();

  const selectedDoc = getSelectedDocument();
  const currentPdf = getCurrentPDF();
  const currentPage = getCurrentPage();

  return (
    <div className="flex flex-col h-full bg-background rounded-lg border-2 border-border">
      {/* Header */}
      <div className="border-b-2 border-border p-4">
        <h2 className="text-lg font-semibold">
          {currentPdf?.name || selectedDoc?.name || 'Document Viewer'}
        </h2>
      </div>

      {/* Viewer content */}
      <div className="flex-1 overflow-y-auto p-4 flex items-center justify-center">
        {currentPage?.imageUrl ? (
          <Image
            src={currentPage.imageUrl}
            alt={`Page ${currentPage.pageNumber}`}
            width={800}
            height={1000}
            className="max-w-full max-h-full object-contain"
          />
        ) : selectedDoc ? (
          <div className="text-center text-muted-foreground">
            <p>{selectedDoc.name}</p>
            <p className="text-xs mt-2">
              PDF preview will appear here.
            </p>
          </div>
        ) : (
          <div className="text-center text-muted-foreground">
            <p>Select a document to view</p>
          </div>
        )}
      </div>

      {/* Footer: Pagination and info */}
      {currentPdf && (
        <div className="border-t-2 border-border p-4 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span>
              Page {currentPage?.pageNumber || 1} of {currentPdf.totalPages}
            </span>
            <span className="text-xs text-muted-foreground">
              {currentPdf.name}
            </span>
          </div>

          <div className="flex gap-2">
            <button
              onClick={previousPage}
              disabled={!currentPage || currentPage.pageNumber === 1}
              className="flex-1 px-3 py-2 rounded-md bg-muted text-sm font-medium hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={nextPage}
              disabled={
                !currentPage || currentPage.pageNumber === currentPdf.totalPages
              }
              className="flex-1 px-3 py-2 rounded-md bg-muted text-sm font-medium hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
