'use client';

import { Settings } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

export default function AppHeader() {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-surface px-6">
      <span className="text-base font-semibold text-foreground">
        PaperLoom
      </span>

      <div className="flex items-center gap-1">
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
