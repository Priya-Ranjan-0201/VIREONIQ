import React from 'react';

interface UiverseCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  glowColor?: 'peach' | 'sky' | 'emerald' | 'neutral';
  interactive?: boolean;
}

export const UiverseCard: React.FC<UiverseCardProps> = ({
  children,
  glowColor = 'neutral',
  interactive = true,
  className = '',
  ...props
}) => {
  const glowBorderClass = {
    peach: 'hover:border-[#fdbcb4]/60 hover:shadow-[0_12px_36px_rgba(253,188,180,0.25)]',
    sky: 'hover:border-[#add8e6]/60 hover:shadow-[0_12px_36px_rgba(173,216,230,0.25)]',
    emerald: 'hover:border-[#22c55e]/60 hover:shadow-[0_12px_36px_rgba(34,197,94,0.25)]',
    neutral: 'hover:border-slate-400/40 dark:hover:border-white/20 hover:shadow-xl',
  }[glowColor];

  return (
    <div
      className={`
        relative overflow-hidden rounded-2xl transition-all duration-300
        bg-white/80 dark:bg-slate-900/70 backdrop-blur-2xl
        border border-slate-200/80 dark:border-white/[0.08]
        shadow-sm dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)]
        ${interactive ? `hover:-translate-y-1 ${glowBorderClass}` : ''}
        ${className}
      `}
      {...props}
    >
      {/* Top subtle ambient highlight */}
      <div className="absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/50 dark:via-white/20 to-transparent pointer-events-none" />
      {children}
    </div>
  );
};
