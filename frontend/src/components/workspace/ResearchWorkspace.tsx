'use client';

import React from 'react';
import DocumentExplorer from './DocumentExplorer';
import ConversationPanel from './ConversationPanel';
import DocumentViewerPanel from './DocumentViewerPanel';
import ThemeToggle from './ThemeToggle';

export default function ResearchWorkspace() {
  return (
    <div className="flex h-screen bg-background">
      {/* Left sidebar: Document Explorer */}
      <aside className="w-64 border-r-2 border-border overflow-y-auto flex flex-col" style={{ backgroundColor: 'var(--explorer-bg)' }}>
        <DocumentExplorer />
        <div className="mt-auto border-t-2 border-border p-4">
          <ThemeToggle />
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex gap-4 p-4">
        {/* Center: Conversation Panel */}
        <div className="flex-1 flex flex-col" style={{ backgroundColor: 'var(--conversation-bg)' }}>
          <ConversationPanel />
        </div>

        {/* Right: Document Viewer Panel */}
        <aside className="w-96 border-l-2 border-border overflow-y-auto" style={{ backgroundColor: 'var(--viewer-bg)' }}>
          <DocumentViewerPanel />
        </aside>
      </div>
    </div>
  );
}
