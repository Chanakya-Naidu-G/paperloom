'use client';

import { useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { FileText, PenLine, X } from 'lucide-react';
import { useChatStore } from '@/store/useChatStore';
import { useDocumentStore } from '@/store/useDocumentStore';
import { formatDate, formatFileSize } from '@/lib/utils';
import { askQuestion } from '@/services/chatServices';
import DocumentViewerPanel from './DocumentViewerPanel';
import { JumpingDots } from '@/components/ui/JumpingDots';

interface ContextPanelProps {
  onClose: () => void;
}

interface RelevantSection {
  id: string;
  section: string;
  page?: number;
}

const VISIBLE_SECTIONS = 3;

const SUMMARY_PROMPT =
  'Provide a concise but comprehensive summary of this paper, covering its purpose, methodology, key concepts, important findings, and conclusions.';

export default function ContextPanel({ onClose }: ContextPanelProps) {
  const [showAllSections, setShowAllSections] = useState(false);
  const [showViewer, setShowViewer] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);

  const selectedDocument = useDocumentStore((state) =>
    state.documents.find(
      (doc) => doc.id === state.selectedDocumentId
    )
  );

  const activeSession = useChatStore((state) =>
    state.sessions.find(
      (session) => session.id === state.activeSessionId
    )
  );

  // Relevant sections come from the citations of the latest assistant answer.
  const relevantSections = useMemo<RelevantSection[]>(() => {
    const messages = activeSession?.messages ?? [];

    for (let i = messages.length - 1; i >= 0; i--) {
      const message = messages[i];

      if (message.role === 'assistant' && message.citations?.length) {
        const seen = new Set<string>();
        const sections: RelevantSection[] = [];

        for (const citation of message.citations) {
          const key = `${citation.source}-${citation.page ?? ''}`;

          if (seen.has(key)) {
            continue;
          }

          seen.add(key);
          sections.push({
            id: citation.id,
            section: citation.source,
            page: citation.page,
          });
        }

        return sections;
      }
    }

    return [];
  }, [activeSession]);

  const visibleSections = showAllSections
    ? relevantSections
    : relevantSections.slice(0, VISIBLE_SECTIONS);

  async function handleSummarize() {
    if (!selectedDocument || isSummarizing) return;

    const documentId = selectedDocument.id;
    const title = selectedDocument.name;
    setIsSummarizing(true);

    const chatStore = useChatStore.getState();
    const session = chatStore.getOrCreateSessionForDocument(documentId, title);
    const sessionId = session.id;

    // Insert user message as the spec expects: "Summarize this paper."
    chatStore.addMessage(sessionId, {
      id: `msg-${Date.now()}-user`,
      role: 'user',
      content: 'Summarize this paper.',
      timestamp: new Date(),
    });

    try {
      const response = await askQuestion({
        query: SUMMARY_PROMPT,
        top_k: 5,
        document_ids: [documentId],
      });

      chatStore.addMessage(sessionId, {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        citations: response.sources.map((source, index) => ({
          id: `${source.chunk_id}-${index}`,
          source: source.section || source.document_id,
          page: source.page_start,
          text: `Pages ${source.page_start}-${source.page_end}`,
        })),
      });
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : 'Failed to summarize. Please try again.';
      chatStore.addMessage(sessionId, {
        id: `msg-${Date.now()}-error`,
        role: 'assistant',
        content: `Sorry, I couldn't summarize that. ${msg}`,
        timestamp: new Date(),
      });
    } finally {
      setIsSummarizing(false);
    }
  }

  return (
    <aside className="flex h-full min-h-0 w-[380px] shrink-0 flex-col overflow-y-auto border-l border-border bg-viewer">
      {/* Panel header */}
      <div className="flex items-center justify-between border-b border-border px-6 py-4 max-[1023px]:px-4">
        <h2 className="text-base font-semibold text-foreground">
          Context
        </h2>

        <motion.button
          type="button"
          onClick={onClose}
          aria-label="Close context panel"
          whileTap={{ scale: 0.85 }}
          className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
        >
          <X className="h-5 w-5" />
        </motion.button>
      </div>

      {!selectedDocument ? (
        <div className="flex flex-1 items-center justify-center px-6 text-center text-xs text-faint max-[1023px]:px-4">
          Select a document to see its context.
        </div>
      ) : (
        <>
          {/* Paper Information */}
          <section className="border-b border-border px-6 py-5 max-[1023px]:px-4">
            <h3 className="text-[13px] font-medium text-foreground">
              Paper Information
            </h3>

            <dl className="mt-4 space-y-3">
              <div className="flex items-center justify-between gap-4">
                <dt className="shrink-0 text-xs text-faint">File Name</dt>
                <dd className="min-w-0 truncate text-[13px] text-foreground">
                  {selectedDocument.name}
                </dd>
              </div>

              <div className="flex items-center justify-between gap-4">
                <dt className="shrink-0 text-xs text-faint">Pages</dt>
                <dd className="text-[13px] text-foreground">
                  {selectedDocument.pages ?? '—'}
                </dd>
              </div>

              <div className="flex items-center justify-between gap-4">
                <dt className="shrink-0 text-xs text-faint">File Size</dt>
                <dd className="text-[13px] text-foreground">
                  {formatFileSize(selectedDocument.size)}
                </dd>
              </div>

              <div className="flex items-center justify-between gap-4">
                <dt className="shrink-0 text-xs text-faint">Uploaded</dt>
                <dd className="text-[13px] text-foreground">
                  {formatDate(selectedDocument.uploadedAt)}
                </dd>
              </div>
            </dl>
          </section>

          {/* Quick Actions */}
          <section className="border-b border-border px-6 py-5 max-[1023px]:px-4">
            <h3 className="text-[13px] font-medium text-foreground">
              Quick Actions
            </h3>

            <div className="mt-4 space-y-3">
              <motion.button
                type="button"
                onClick={() => setShowViewer(true)}
                whileTap={{ scale: 0.98 }}
                className="flex h-10 w-full items-center gap-3 rounded-lg border border-border px-4 text-[13px] font-medium text-foreground transition-colors hover:bg-surface-2 motion-safe:transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
              >
                <FileText className="h-4 w-4 text-muted-foreground" />
                View PDF
              </motion.button>

              <motion.button
                type="button"
                onClick={handleSummarize}
                disabled={isSummarizing}
                whileTap={isSummarizing ? undefined : { scale: 0.98 }}
                className="flex h-10 w-full items-center gap-3 rounded-lg border border-border px-4 text-[13px] font-medium text-foreground transition-colors hover:bg-surface-2 disabled:cursor-not-allowed disabled:opacity-60 motion-safe:transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
              >
                {isSummarizing ? (
                  <JumpingDots />
                ) : (
                  <PenLine className="h-4 w-4 text-muted-foreground" />
                )}
                {isSummarizing ? 'Summarizing...' : 'Summarize Paper'}
              </motion.button>
            </div>
          </section>

          {/* Relevant Sections */}
          <section className="px-6 py-5 max-[1023px]:px-4">
            <h3 className="text-[13px] font-medium text-foreground">
              Relevant Sections
            </h3>

            {relevantSections.length === 0 ? (
              <p className="mt-4 text-xs text-faint">
                Ask a question to see the sections used for answering.
              </p>
            ) : (
              <>
                <div className="mt-4 space-y-1">
                  {visibleSections.map((section) => (
                    <div
                      key={section.id}
                      className="flex items-center justify-between gap-4 py-1.5"
                    >
                      <span className="min-w-0 truncate text-[13px] text-foreground">
                        {section.section}
                      </span>

                      {section.page !== undefined && (
                        <span className="shrink-0 text-xs text-muted-foreground">
                          Page {section.page}
                        </span>
                      )}
                    </div>
                  ))}
                </div>

                {relevantSections.length > VISIBLE_SECTIONS && (
                  <motion.button
                    type="button"
                    onClick={() =>
                      setShowAllSections((prev) => !prev)
                    }
                    whileTap={{ scale: 0.98 }}
                    className="mt-4 flex h-10 w-full items-center justify-center rounded-lg border border-border text-[13px] font-medium text-foreground transition-colors hover:bg-surface-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
                  >
                    {showAllSections
                      ? 'Show Fewer Sections'
                      : 'Show More Sections'}
                  </motion.button>
                )}
              </>
            )}
          </section>
        </>
      )}

      {/* PDF Viewer Overlay — document-specific, close independent from page count.
          AnimatePresence gives a real exit transition (CSS animate-in cannot). */}
      <AnimatePresence>
        {showViewer && selectedDocument && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          >
            <div
              className="absolute inset-0"
              onClick={() => setShowViewer(false)}
              aria-hidden
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, filter: 'blur(8px)' }}
              animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
              exit={{ opacity: 0, scale: 0.95, filter: 'blur(8px)' }}
              transition={{ duration: 0.2, delay: 0.05 }}
              className="relative flex h-[85vh] w-full max-w-4xl flex-col overflow-hidden rounded-xl border border-border bg-background shadow-2xl max-[765px]:h-[90vh] max-[765px]:max-w-[95vw]"
            >
              <DocumentViewerPanel onClose={() => setShowViewer(false)} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </aside>
  );
}
