'use client';

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  username: string | null;
  hasHydrated: boolean;

  setAuth: (token: string, username: string) => void;
  clearAuth: () => void;
  setHasHydrated: (value: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      username: null,
      hasHydrated: false,

      setAuth: (token, username) =>
        set({
          token,
          username,
        }),

      clearAuth: () =>
        set({
          token: null,
          username: null,
        }),

      setHasHydrated: (value) =>
        set({
          hasHydrated: value,
        }),
    }),
    {
      name: 'paperloom-auth',

      storage: createJSONStorage(() => {
        if (typeof window !== 'undefined') {
          return window.localStorage;
        }

        return {
          getItem: () => null,
          setItem: () => {},
          removeItem: () => {},
        } as unknown as Storage;
      }),

      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    },
  ),
);