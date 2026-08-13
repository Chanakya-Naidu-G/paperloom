'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState<boolean | null>(null);

  const applyTheme = useCallback((dark: boolean) => {
    const html = document.documentElement;
    if (dark) {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  }, []);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedTheme ? savedTheme === 'dark' : prefersDark;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsDark(shouldBeDark);
    applyTheme(shouldBeDark);
  }, [applyTheme]);

  const toggleTheme = useCallback(() => {
    setIsDark((prev) => {
      if (prev === null) return true;
      const newIsDark = !prev;
      applyTheme(newIsDark);
      return newIsDark;
    });
  }, [applyTheme]);

  if (isDark === null) return null;

  return (
    <button
      onClick={toggleTheme}
      className="p-3 rounded-lg border-2 border-border bg-muted hover:bg-muted/80 transition-colors flex items-center justify-center"
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-label="Toggle theme"
    >
      {isDark ? (
        <Sun className="w-5 h-5 text-accent" />
      ) : (
        <Moon className="w-5 h-5 text-primary" />
      )}
    </button>
  );
}
