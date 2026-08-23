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
      <AppHeader />

      <div className="flex min-h-0 flex-1">

        {/* Document Explorer */}
        <aside className="w-[260px] shrink-0 max-[1279px]:w-[220px] max-[1023px]:w-[200px] max-[767px]:hidden">
          <DocumentExplorer />
        </aside>

        {/* Conversation */}
        <main className="min-w-0 flex-1">
          <ConversationPanel />
        </main>

        {/* Context */}
        <aside className="hidden shrink-0 min-[1024px]:block">
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
    </div>
  );
}