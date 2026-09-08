'use client';

import { MotionConfig } from 'motion/react';
import type { ReactNode } from 'react';

/* Global Motion config: respects OS prefers-reduced-motion everywhere,
 * replacing the need for per-element motion-safe: prefixes on new code. */
export function MotionProvider({ children }: { children: ReactNode }) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}
