'use client';

import React, { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
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
              <motion.button
                type="button"
                onClick={() => setIsContextOpen(true)}
                aria-label="Open context panel"
                title="Open context panel"
                whileTap={{ scale: 0.85 }}
                className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
              >
                <PanelRight className="h-5 w-5" />
              </motion.button>
            </div>
          )}
        </aside>
      </div>

      {/* Mobile documents drawer — AnimatePresence so close animates out */}
      <AnimatePresence>
        {isDocsDrawerOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex"
          >
            <div
              className="absolute inset-0 bg-black/60"
              onClick={() => setIsDocsDrawerOpen(false)}
            />

            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', bounce: 0, duration: 0.35 }}
              className="relative flex h-full w-[260px] max-w-[85vw] flex-col bg-explorer shadow-xl"
            >
              <DocumentExplorer />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mobile context drawer */}
      <AnimatePresence>
        {isContextDrawerOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex justify-end"
          >
            <div
              className="absolute inset-0 bg-black/60"
              onClick={() => setIsContextDrawerOpen(false)}
            />

            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', bounce: 0, duration: 0.35 }}
              className="relative flex h-full w-[380px] max-w-[85vw] flex-col overflow-hidden bg-viewer shadow-xl"
            >
              <ContextPanel
                onClose={() => setIsContextDrawerOpen(false)}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
