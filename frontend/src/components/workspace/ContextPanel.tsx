'use client';

import { useMemo, useState } from 'react';
import { FileText, Link2, PenLine, X } from 'lucide-react';
import { useChatStore } from '@/store/useChatStore';
import { useDocumentStore } from '@/store/useDocumentStore';
import { formatDate, formatFileSize } from '@/lib/utils';

interface ContextPanelProps {
  onClose: () => void;
}

interface RelevantSection {
  id: string;
  section: string;
  page?: number;
}

const VISIBLE_SECTIONS = 3;

export default function ContextPanel({ onClose }: ContextPanelProps) {
  const [showAllSections, setShowAllSections] = useState(false);

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

  return (
    <aside className="flex w-[380px] shrink-0 flex-col overflow-y-auto border-l border-border bg-viewer">
      {/* Panel header */}
      <div className="flex items-center justify-between border-b border-border px-6 py-4 max-[1023px]:px-4">
        <h2 className="text-base font-semibold text-foreground">
          Context
        </h2>

        <button
          type="button"
          onClick={onClose}
          aria-label="Close context panel"
          className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
        >
          <X className="h-5 w-5" />
        </button>
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
              <button
                type="button"
                className="flex h-10 w-full items-center gap-3 rounded-lg border border-border px-4 text-[13px] font-medium text-foreground transition-colors hover:bg-surface-2"
              >
                <FileText className="h-4 w-4 text-muted-foreground" />
                View PDF
              </button>

              <button
                type="button"
                className="flex h-10 w-full items-center gap-3 rounded-lg border border-border px-4 text-[13px] font-medium text-foreground transition-colors hover:bg-surface-2"
              >
                <Link2 className="h-4 w-4 text-muted-foreground" />
                Extract References
              </button>

              <button
                type="button"
                className="flex h-10 w-full items-center gap-3 rounded-lg border border-border px-4 text-[13px] font-medium text-foreground transition-colors hover:bg-surface-2"
              >
                <PenLine className="h-4 w-4 text-muted-foreground" />
                Summarize Paper
              </button>
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
                  <button
                    type="button"
                    onClick={() =>
                      setShowAllSections((prev) => !prev)
                    }
                    className="mt-4 flex h-10 w-full items-center justify-center rounded-lg border border-border text-[13px] font-medium text-foreground transition-colors hover:bg-surface-2"
                  >
                    {showAllSections
                      ? 'Show Fewer Sections'
                      : 'Show More Sections'}
                  </button>
                )}
              </>
            )}
          </section>
        </>
      )}
    </aside>
  );
}
