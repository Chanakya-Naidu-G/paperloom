'use client';

import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { LogOut } from 'lucide-react';
import { contentAnimations } from '@/components/ui/AnimatedReveal';

/* Template 2 (UserButton) applied to PaperLoom auth state.
 * The closed avatar button and the open menu are two static layouts;
 * Motion morphs between them via a shared `layoutId` on each container
 * (and a second on the avatar), so there is no manual width/height
 * animation to maintain. Menu content fades via AnimatePresence + blur. */
export function UserMenu({
  username,
  onSignOut,
}: {
  username: string | null;
  onSignOut: () => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const initials = (username ?? '?').trim().slice(0, 2).toUpperCase() || '?';

  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: PointerEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('pointerdown', onPointerDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('pointerdown', onPointerDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open ]);

  return (
    <div ref={ref} className="relative">
      <motion.button
        type="button"
        layoutId="user-menu-container"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? 'Close account menu' : 'Open account menu'}
        aria-expanded={open}
        title={username ? `Account (${username})` : 'Account'}
        whileTap={{ scale: 0.9 }}
        transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
        className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
      >
        <motion.span layoutId="user-menu-avatar" className="flex items-center justify-center">
          {initials}
        </motion.span>
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            layoutId="user-menu-container"
            transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
            className="absolute right-0 top-11 z-50 w-56 overflow-hidden rounded-xl border border-border bg-surface shadow-xl"
          >
            <motion.div
              {...contentAnimations}
              className="p-2"
            >
              <div className="flex items-center gap-3 rounded-lg px-2 py-2">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                  {initials}
                </span>
                <div className="min-w-0">
                  <p className="truncate text-[13px] font-medium text-foreground">{username}</p>
                  <p className="truncate text-[11px] text-muted-foreground">PaperLoom account</p>
                </div>
              </div>
              <motion.button
                type="button"
                onClick={() => {
                  setOpen(false);
                  onSignOut();
                }}
                whileTap={{ scale: 0.98 }}
                className="mt-1 flex h-9 w-full items-center gap-2 rounded-lg px-2 text-[13px] font-medium text-foreground transition-colors hover:bg-surface-2"
              >
                <LogOut className="h-4 w-4 text-muted-foreground" />
                Sign out
              </motion.button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
