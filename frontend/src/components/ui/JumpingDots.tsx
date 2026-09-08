'use client';

import { motion, MotionConfig, type Variants } from 'motion/react';

/* Template 3 adaptation — Loading jumping dots.
 * Same staggerChildren mirror-jump physics as the reference; colors and
 * sizes are adapted to the PaperLoom theme via currentColor so the dots
 * inherit the button text color wherever they are placed. */
const dotVariants: Variants = {
  jump: {
    transform: 'translateY(-30%)',
    transition: {
      duration: 0.5,
      repeat: Infinity,
      repeatType: 'mirror',
      ease: 'easeInOut',
    },
  },
};

export function JumpingDots({ className = '' }: { className?: string }) {
  return (
    <MotionConfig reducedMotion="user">
      <motion.span
        animate="jump"
        transition={{ staggerChildren: -0.15, staggerDirection: -1 }}
        className={`inline-flex items-center gap-1 ${className}`}
        aria-hidden
      >
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            variants={dotVariants}
            className="h-1.5 w-1.5 rounded-full bg-current"
          />
        ))}
      </motion.span>
    </MotionConfig>
  );
}
