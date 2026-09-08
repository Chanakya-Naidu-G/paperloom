'use client';

import { AnimatePresence, motion, MotionConfig } from 'motion/react';
import type { ReactNode } from 'react';

/* Template 2 adaptation — Clerk UserButton layoutId morph.
 * The original morphs a closed button and an open menu via a shared
 * `layoutId` on each container (plus one on the avatar), with menu
 * content fading via AnimatePresence + blur. This wrapper gives any
 * binary icon swap (Eye/EyeOff, Sun/Moon, ArrowUp/loader) the same
 * treatment: the icons crossfade with blur while the button itself
 * morphs with a spring, so no manual width/height animation is needed. */
export function MorphIcon({
  iconKey,
  children,
  layoutId,
  className,
}: {
  iconKey: string;
  children: ReactNode;
  layoutId: string;
  className?: string;
}) {
  return (
    <MotionConfig reducedMotion="user">
      <motion.span layoutId={layoutId} className={className} transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}>
        <AnimatePresence mode="wait" initial={false}>
          <motion.span
            key={iconKey}
            initial={{ opacity: 0, filter: 'blur(4px)', scale: 0.8 }}
            animate={{ opacity: 1, filter: 'blur(0px)', scale: 1 }}
            exit={{ opacity: 0, filter: 'blur(4px)', scale: 0.8 }}
            transition={{ duration: 0.15 }}
            className="flex items-center justify-center"
          >
            {children}
          </motion.span>
        </AnimatePresence>
      </motion.span>
    </MotionConfig>
  );
}
