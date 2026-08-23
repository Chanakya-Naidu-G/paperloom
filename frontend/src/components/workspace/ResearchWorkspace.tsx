'use client';

import React, { useState } from 'react';
import { PanelRight } from 'lucide-react';
import AppHeader from './AppHeader';
import DocumentExplorer from './DocumentExplorer';
import ConversationPanel from './ConversationPanel';
import ContextPanel from './ContextPanel';

export default function ResearchWorkspace() {
  const [isContextOpen, setIsContextOpen] = useState(true);

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      {/* Header: 1440 × 64 · #0F0F12 · border-b #27272A */}
      <AppHeader />

      <div className="flex min-h-0 flex-1">
        {/* Document Explorer: 260 × 960 · #0F0F12 · border-r #27272A */}
        <DocumentExplorer />

        {/* Conversation Panel: 800 × 960 · #08080E */}
        <ConversationPanel />

        {/* Context Panel: 380 × 960 · #0F0F12 · border-l #27272A */}
        {isContextOpen ? (
          <ContextPanel onClose={() => setIsContextOpen(false)} />
        ) : (
          <div className="flex w-12 shrink-0 items-start justify-center border-l border-border bg-viewer pt-4">
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
      </div>
    </div>
  );
}
