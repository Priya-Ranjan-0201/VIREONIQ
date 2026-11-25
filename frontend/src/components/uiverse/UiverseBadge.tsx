import React from 'react';

interface UiverseBadgeProps {
  children: React.ReactNode;
  variant?: 'peach' | 'sky' | 'emerald' | 'cosmic' | 'neutral';
  pulseDot?: boolean;
  className?: string;
}

export const UiverseBadge: React.FC<UiverseBadgeProps> = ({
  children,
  variant = 'cosmic',
  pulseDot = false,
  className = '',
}) => {
  const styles = {
    peach: {
      container: 'bg-[#fdbcb4]/15 border-[#fdbcb4]/40 text-rose-700 dark:text-[#fdbcb4] shadow-[0_0_12px_rgba(253,188,180,0.25)]',
      dot: 'bg-[#fdbcb4] shadow-[0_0_8px_#fdbcb4]',
    },
    sky: {
      container: 'bg-[#add8e6]/20 border-[#add8e6]/45 text-sky-800 dark:text-[#add8e6] shadow-[0_0_12px_rgba(173,216,230,0.25)]',
      dot: 'bg-[#add8e6] shadow-[0_0_8px_#add8e6]',
    },
    emerald: {
      container: 'bg-[#22c55e]/15 border-[#22c55e]/35 text-emerald-800 dark:text-[#4ade80] shadow-[0_0_12px_rgba(34,197,94,0.25)]',
      dot: 'bg-[#22c55e] shadow-[0_0_8px_#22c55e]',
    },
    cosmic: {
      container: 'bg-gradient-to-r from-[#fdbcb4]/15 via-[#add8e6]/15 to-[#22c55e]/15 border-white/20 text-slate-800 dark:text-white shadow-[0_0_16px_rgba(173,216,230,0.3)]',
      dot: 'bg-gradient-to-r from-[#fdbcb4] to-[#22c55e] shadow-[0_0_8px_#add8e6]',
    },
    neutral: {
      container: 'bg-slate-100 dark:bg-white/[0.05] border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300',
      dot: 'bg-slate-400 dark:bg-slate-500',
    },
  }[variant];

  return (
    <span
      className={`
        relative inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-full whitespace-nowrap shrink-0
        border backdrop-blur-md transition-all duration-300 select-none overflow-hidden
        ${styles.container}
        ${className}
      `}
    >
      {/* Metallic holographic shimmer highlight */}
      <span className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/50 to-transparent" />
      {pulseDot && (
        <span className="relative flex h-2 w-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${styles.dot}`} />
          <span className={`relative inline-flex rounded-full h-2 w-2 ${styles.dot}`} />
        </span>
      )}
      <span>{children}</span>
    </span>
  );
};
