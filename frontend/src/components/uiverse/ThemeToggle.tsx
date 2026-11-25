import React from 'react';
import { useThemeStore } from '@/store/themeStore';
import { Sun, Moon, Sparkles } from 'lucide-react';

interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = '', showLabel = false }) => {
  const { mode, toggleTheme } = useThemeStore();
  const isDark = mode === 'dark';

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      {/* Uiverse.io Inspired Celestial Sun/Moon Toggle */}
      <button
        type="button"
        role="switch"
        aria-checked={isDark}
        aria-label="Toggle dark/light theme"
        onClick={toggleTheme}
        className={`
          group relative w-16 h-8 rounded-full p-1 transition-all duration-500 ease-out cursor-pointer
          border shadow-lg select-none outline-none focus-visible:ring-2 focus-visible:ring-offset-2
          ${isDark
            ? 'bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border-indigo-500/40 shadow-[0_0_15px_rgba(173,216,230,0.25)] focus-visible:ring-sky-400'
            : 'bg-gradient-to-r from-amber-100 via-sky-100 to-rose-100 border-[#fdbcb4]/60 shadow-[0_0_15px_rgba(253,188,180,0.4)] focus-visible:ring-[#fdbcb4]'
          }
        `}
      >
        {/* Sky Ambient Elements inside track */}
        <div className="absolute inset-0 rounded-full overflow-hidden pointer-events-none">
          {/* Day Clouds */}
          <div
            className={`absolute top-1 left-2 transition-all duration-500 ease-out ${
              isDark ? 'opacity-0 -translate-y-4 scale-50' : 'opacity-80 translate-y-0 scale-100'
            }`}
          >
            <span className="block w-2.5 h-1.5 bg-white/90 rounded-full blur-[0.3px]" />
          </div>
          {/* Night Stars */}
          <div
            className={`absolute top-1.5 right-2 flex gap-1 transition-all duration-500 ease-out ${
              isDark ? 'opacity-90 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-50'
            }`}
          >
            <Sparkles className="w-2.5 h-2.5 text-[#add8e6] animate-pulse" />
          </div>
        </div>

        {/* Sliding Celestial Orb */}
        <div
          className={`
            relative w-6 h-6 rounded-full transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]
            flex items-center justify-center shadow-md transform
            ${isDark
              ? 'translate-x-8 bg-gradient-to-tr from-sky-400 to-[#add8e6] text-slate-950 shadow-[0_0_10px_#add8e6]'
              : 'translate-x-0 bg-gradient-to-tr from-[#fdbcb4] to-amber-300 text-amber-950 shadow-[0_0_10px_#fdbcb4]'
            }
          `}
        >
          {isDark ? (
            <Moon className="w-3.5 h-3.5 transition-transform duration-500 rotate-0 group-hover:-rotate-12 fill-slate-950/20" />
          ) : (
            <Sun className="w-3.5 h-3.5 transition-transform duration-500 rotate-0 group-hover:rotate-45" />
          )}
        </div>
      </button>

      {showLabel && (
        <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 transition-colors">
          {isDark ? 'Dark Mode' : 'Light Mode'}
        </span>
      )}
    </div>
  );
};
