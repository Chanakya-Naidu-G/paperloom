'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Eye, EyeOff, FileText, Loader2 } from 'lucide-react';
import { loginUser, registerUser } from '@/services/authService';
import { useAuthStore } from '@/store/useAuthStore';
import ThemeToggle from '@/components/workspace/ThemeToggle';

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{ username?: string; password?: string }>({});
  const [loading, setLoading] = useState(false);

  function validate(): boolean {
    const errs: typeof fieldErrors = {};
    if (username.trim().length < 3) errs.username = 'At least 3 characters (letters, digits, _).';
    else if (!/^[a-zA-Z0-9_]+$/.test(username.trim())) errs.username = 'Only letters, digits, underscores.';
    if (password.length < 6) errs.password = 'At least 6 characters.';
    setFieldErrors(errs);
    if (Object.keys(errs).length) {
      setError(mode === 'login' ? 'Please fix the highlighted fields.' : 'Please fix the highlighted fields.');
      return false;
    }
    return true;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!validate()) return;
    setLoading(true);
    try {
      const action = mode === 'login' ? loginUser : registerUser;
      const data = await action({ username: username.trim(), password });
      setAuth(data.access_token, data.username);
      router.replace('/workspace');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-background px-4 py-8 motion-safe:animate-in motion-safe:fade-in motion-safe:duration-500">
      <div className="absolute right-4 top-4">
        <ThemeToggle />
      </div>
      <div className="w-full max-w-sm motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-2 motion-safe:duration-300">
        <div className="rounded-2xl border border-border bg-surface p-8 shadow-xl shadow-black/20">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight text-foreground">PaperLoom</h1>
              <p className="text-xs text-muted-foreground">Research, organized</p>
            </div>
          </div>

          <h2 className="mt-6 text-[15px] font-semibold text-foreground">
            {mode === 'login' ? 'Welcome back' : 'Create account'}
          </h2>
          <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
            {mode === 'login' ? 'Sign in to continue to your workspace.' : 'Join PaperLoom to chat with your papers.'}
          </p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-foreground">Username</label>
              <input
                value={username}
                onChange={(e) => { setUsername(e.target.value); setFieldErrors((f) => ({ ...f, username: undefined })); }}
                placeholder="e.g. alex_42"
                autoComplete="username"
                aria-invalid={!!fieldErrors.username}
                className={`w-full rounded-xl border bg-background px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 ${fieldErrors.username ? 'border-red-500/60 focus:ring-red-500/30' : 'border-border'}`}
              />
              {fieldErrors.username && <p className="mt-1.5 text-xs text-red-400 motion-safe:animate-in motion-safe:fade-in">{fieldErrors.username}</p>}
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-foreground">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setFieldErrors((f) => ({ ...f, password: undefined })); }}
                  placeholder="••••••••"
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  aria-invalid={!!fieldErrors.password}
                  className={`w-full rounded-xl border bg-background px-3.5 py-2.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 ${fieldErrors.password ? 'border-red-500/60 focus:ring-red-500/30' : 'border-border'}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-muted-foreground hover:bg-surface-2 hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {fieldErrors.password ? (
                <p className="mt-1.5 text-xs text-red-400 motion-safe:animate-in motion-safe:fade-in">{fieldErrors.password}</p>
              ) : (
                <p className="mt-1.5 text-xs text-faint">Min 6 characters</p>
              )}
            </div>

            {error && (
              <div className="rounded-xl border border-red-500/40 bg-red-500/10 px-3 py-2.5 text-xs leading-relaxed text-red-400 motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-top-1">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin" />}
              {loading ? (mode === 'login' ? 'Signing in...' : 'Creating account...') : mode === 'login' ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-muted-foreground">
            {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}{' '}
            <button
              type="button"
              onClick={() => {
                setMode(mode === 'login' ? 'register' : 'login');
                setError(null);
                setFieldErrors({});
              }}
              className="font-medium text-primary hover:underline"
            >
              {mode === 'login' ? 'Register' : 'Sign in'}
            </button>
          </p>
        </div>
        <p className="mt-4 text-center text-xs text-faint">Secure by design • Per-user isolation</p>
      </div>
    </div>
  );
}
