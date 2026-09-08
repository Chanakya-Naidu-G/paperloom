'use client';

import { AnimatePresence, motion, MotionConfig } from 'motion/react';
import type { ReactNode } from 'react';

/* Template 1 adaptation — Clerk ConditionalField.
 * The original animates a password field's measured height with Motion's
 * resize() util so the reveal stays smooth regardless of validation
 * messages below it. Here `height: 'auto'` gives the same measured-height
 * reveal for any conditional block (field errors, server banners), with
 * AnimatePresence so exits animate too (CSS animate-in cannot do exits). */
export function AnimatedReveal({
  open,
  children,
  className,
}: {
  open: boolean;
  children: ReactNode;
  className?: string;
}) {
  return (
    <MotionConfig reducedMotion="user">
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="reveal"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22, ease: 'easeInOut' }}
            className={`overflow-hidden ${className ?? ''}`}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </MotionConfig>
  );
}

/* Shared blur fade used for swapped content (headings, menu bodies),
 * taken from the UserButton template's contentAnimations. */
export const contentAnimations = {
  initial: { opacity: 0, filter: 'blur(8px)' },
  animate: { opacity: 1, filter: 'blur(0px)', transition: { delay: 0.15 } },
  exit: { opacity: 0, filter: 'blur(8px)' },
};
