import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemeMode = 'dark' | 'light';

interface ThemeState {
  mode: ThemeMode;
  toggleTheme: () => void;
  setTheme: (mode: ThemeMode) => void;
}

const applyThemeToDOM = (mode: ThemeMode) => {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  if (mode === 'dark') {
    root.classList.add('dark');
    root.classList.remove('light');
    root.style.colorScheme = 'dark';
  } else {
    root.classList.add('light');
    root.classList.remove('dark');
    root.style.colorScheme = 'light';
  }
};

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: 'dark', // Default to futuristic dark mode
      toggleTheme: () => {
        const nextMode = get().mode === 'dark' ? 'light' : 'dark';
        applyThemeToDOM(nextMode);
        set({ mode: nextMode });
      },
      setTheme: (mode: ThemeMode) => {
        applyThemeToDOM(mode);
        set({ mode });
      },
    }),
    {
      name: 'vireoniq-theme-mode',
      onRehydrateStorage: () => (state) => {
        if (state) {
          applyThemeToDOM(state.mode);
        } else {
          applyThemeToDOM('dark');
        }
      },
    }
  )
);

// Initial application on script evaluation
if (typeof document !== 'undefined') {
  try {
    const stored = localStorage.getItem('vireoniq-theme-mode');
    if (stored) {
      const parsed = JSON.parse(stored);
      applyThemeToDOM(parsed?.state?.mode || 'dark');
    } else {
      applyThemeToDOM('dark');
    }
  } catch {
    applyThemeToDOM('dark');
  }
}
