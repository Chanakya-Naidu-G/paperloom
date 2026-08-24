'use client';

import { Menu, PanelRight, Settings } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

interface AppHeaderProps {
  onOpenDocuments?: () => void;
  onOpenContext?: () => void;
}

export default function AppHeader({
  onOpenDocuments,
  onOpenContext,
}: AppHeaderProps) {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-surface px-6 max-[1023px]:px-4 max-[767px]:px-3">
      <div className="flex min-w-0 items-center gap-1">
        {/* Mobile only: documents drawer */}
        <button
          type="button"
          onClick={() => onOpenDocuments?.()}
          aria-label="Open documents"
          title="Documents"
          className="hidden h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground max-[767px]:flex"
        >
          <Menu className="h-5 w-5" />
        </button>

        <span className="truncate text-base font-semibold text-foreground">
          PaperLoom
        </span>
      </div>

      <div className="flex shrink-0 items-center gap-1">
        {/* Mobile only: context drawer */}
        <button
          type="button"
          onClick={() => onOpenContext?.()}
          aria-label="Open context panel"
          title="Context"
          className="hidden h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground max-[767px]:flex"
        >
          <PanelRight className="h-5 w-5" />
        </button>

        <ThemeToggle />

        <button
          type="button"
          aria-label="Settings"
          title="Settings"
          className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
        >
          <Settings className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
