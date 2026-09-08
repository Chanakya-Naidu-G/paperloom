'use client';

import { Menu, PanelRight } from 'lucide-react';
import { motion } from 'motion/react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { useChatStore } from '@/store/useChatStore';
import { useDocumentStore } from '@/store/useDocumentStore';
import ThemeToggle from './ThemeToggle';
import { UserMenu } from './UserMenu';

interface AppHeaderProps {
  onOpenDocuments?: () => void;
  onOpenContext?: () => void;
}

export default function AppHeader({
  onOpenDocuments,
  onOpenContext,
}: AppHeaderProps) {
  const router = useRouter();
  const username = useAuthStore((s) => s.username);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  function handleLogout() {
    // Clear all user-scoped client state so back-nav cannot flash protected data
    useDocumentStore.getState().clearAllDocuments();
    // wipe chat sessions
    useChatStore.setState({ sessions: [], activeSessionId: null });
    clearAuth();
    router.replace('/login');
  }
  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-surface px-6 max-[1023px]:px-4 max-[767px]:px-3">
      <div className="flex min-w-0 items-center gap-1">
        {/* Mobile only: documents drawer */}
        <motion.button
          type="button"
          onClick={() => onOpenDocuments?.()}
          aria-label="Open documents"
          title="Documents"
          whileTap={{ scale: 0.85 }}
          className="hidden h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 max-[767px]:flex"
        >
          <Menu className="h-5 w-5" />
        </motion.button>

        <span className="truncate text-base font-semibold text-foreground">
          PaperLoom
        </span>
      </div>

      <div className="flex shrink-0 items-center gap-1">
        {/* Mobile only: context drawer */}
        <motion.button
          type="button"
          onClick={() => onOpenContext?.()}
          aria-label="Open context panel"
          title="Context"
          whileTap={{ scale: 0.85 }}
          className="hidden h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 max-[767px]:flex"
        >
          <PanelRight className="h-5 w-5" />
        </motion.button>

        <ThemeToggle />

        {username && (
          <span className="hidden max-w-[120px] truncate text-xs text-muted-foreground max-[900px]:hidden">
            {username}
          </span>
        )}

        <UserMenu username={username} onSignOut={handleLogout} />
      </div>
    </header>
  );
}
