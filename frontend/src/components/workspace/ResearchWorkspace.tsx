'use client';

import React, { useState } from 'react';
import { PanelRight } from 'lucide-react';
import AppHeader from './AppHeader';
import DocumentExplorer from './DocumentExplorer';
import ConversationPanel from './ConversationPanel';
import ContextPanel from './ContextPanel';

export default function ResearchWorkspace() {
  const [isContextOpen, setIsContextOpen] = useState(true);
  const [isDocsDrawerOpen, setIsDocsDrawerOpen] = useState(false);
  const [isContextDrawerOpen, setIsContextDrawerOpen] = useState(false);

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      <AppHeader
        onOpenDocuments={() => setIsDocsDrawerOpen(true)}
        onOpenContext={() => setIsContextDrawerOpen(true)}
      />

      <div className="flex min-h-0 flex-1">
        {/* Document Explorer — divider is an overlay so the 1px border
            never consumes layout space (spec: W 260 incl. border, cards 228) */}
        <aside className="relative w-[260px] shrink-0 max-[1279px]:w-[220px] max-[1023px]:w-[200px] max-[767px]:hidden">
          <span
            aria-hidden
            className="absolute inset-y-0 right-0 w-px bg-border"
          />
          <DocumentExplorer />
        </aside>

        {/* Conversation */}
        <main className="min-w-0 flex-1">
          <ConversationPanel />
        </main>

        {/* Context */}
        <aside className="hidden shrink-0 min-[1024px]:flex">
          {isContextOpen ? (
            <ContextPanel
              onClose={() => setIsContextOpen(false)}
            />
          ) : (
            <div className="flex w-12 items-start justify-center border-l border-border bg-viewer pt-4">
              <button
                type="button"
                onClick={() => setIsContextOpen(true)}
                aria-label="Open context panel"
                title="Open context panel"
                className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
              >
                <PanelRight className="h-5 w-5" />
              </button>
            </div>
          )}
        </aside>
      </div>

      {/* Mobile documents drawer */}
      {isDocsDrawerOpen && (
        <div className="fixed inset-0 z-50 flex motion-safe:animate-in motion-safe:fade-in motion-safe:duration-200">
          <div
            className="absolute inset-0 bg-black/60 motion-safe:animate-in motion-safe:fade-in motion-safe:duration-200"
            onClick={() => setIsDocsDrawerOpen(false)}
          />

          <div className="relative flex h-full w-[260px] max-w-[85vw] flex-col bg-explorer shadow-xl motion-safe:animate-in motion-safe:slide-in-from-left motion-safe:duration-200">
            <DocumentExplorer />
          </div>
        </div>
      )}

      {/* Mobile context drawer */}
      {isContextDrawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end motion-safe:animate-in motion-safe:fade-in motion-safe:duration-200">
          <div
            className="absolute inset-0 bg-black/60 motion-safe:animate-in motion-safe:fade-in motion-safe:duration-200"
            onClick={() => setIsContextDrawerOpen(false)}
          />

          <div className="relative flex h-full w-[380px] max-w-[85vw] flex-col overflow-hidden bg-viewer shadow-xl motion-safe:animate-in motion-safe:slide-in-from-right motion-safe:duration-200">
            <ContextPanel
              onClose={() => setIsContextDrawerOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
