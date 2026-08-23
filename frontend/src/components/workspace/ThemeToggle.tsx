'use client';

import { useEffect, useState, useCallback } from 'react';
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
    // Default to the Figma dark theme on first visit.
    const shouldBeDark = savedTheme ? savedTheme === 'dark' : true;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsDark(shouldBeDark);
    applyTheme(shouldBeDark);
  }, [applyTheme]);

  const toggleTheme = useCallback(() => {
    setIsDark((prev) => {
      if (prev === null) return false;
      const newIsDark = !prev;
      applyTheme(newIsDark);
      return newIsDark;
    });
  }, [applyTheme]);

  if (isDark === null) {
    return (
      <button
        type="button"
        aria-label="Toggle theme"
        className="flex h-9 w-9 items-center justify-center rounded-md"
      />
    );
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-label="Toggle theme"
    >
      {isDark ? (
        <Moon className="h-5 w-5" />
      ) : (
        <Sun className="h-5 w-5" />
      )}
    </button>
  );
}
