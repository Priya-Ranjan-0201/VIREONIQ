import React from 'react';

interface UiverseButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'cosmic' | 'peach' | 'sky' | 'emerald' | 'glass';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export const UiverseButton: React.FC<UiverseButtonProps> = ({
  variant = 'cosmic',
  size = 'md',
  icon,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const sizeClasses = {
    sm: 'px-3.5 py-1.5 text-xs rounded-xl gap-1.5',
    md: 'px-5 py-2.5 text-sm rounded-xl gap-2',
    lg: 'px-7 py-3.5 text-base rounded-2xl gap-2.5 font-bold',
  }[size];

  const variantClasses = {
    cosmic: `
      bg-gradient-to-r from-[#fdbcb4] via-[#add8e6] to-[#22c55e] text-slate-950 font-bold
      shadow-[0_0_24px_rgba(253,188,180,0.35)] hover:shadow-[0_0_36px_rgba(173,216,230,0.65)]
      border border-white/40 hover:scale-[1.02] active:scale-[0.98]
    `,
    peach: `
      bg-[#fdbcb4] text-slate-950 font-bold
      shadow-[0_0_20px_rgba(253,188,180,0.45)] hover:shadow-[0_0_32px_rgba(253,188,180,0.75)]
      border border-white/50 hover:bg-[#fca59b] hover:scale-[1.02] active:scale-[0.98]
    `,
    sky: `
      bg-[#add8e6] text-slate-950 font-bold
      shadow-[0_0_20px_rgba(173,216,230,0.45)] hover:shadow-[0_0_32px_rgba(173,216,230,0.75)]
      border border-white/50 hover:bg-[#93c5fd] hover:scale-[1.02] active:scale-[0.98]
    `,
    emerald: `
      bg-[#22c55e] text-white font-bold
      shadow-[0_0_20px_rgba(34,197,94,0.4)] hover:shadow-[0_0_32px_rgba(34,197,94,0.7)]
      border border-emerald-400/50 hover:bg-[#16a34a] hover:scale-[1.02] active:scale-[0.98]
    `,
    glass: `
      bg-white/10 dark:bg-white/[0.06] text-slate-800 dark:text-white font-semibold backdrop-blur-xl
      border border-slate-300 dark:border-white/10 hover:border-[#add8e6]/60
      shadow-sm hover:shadow-[0_0_20px_rgba(173,216,230,0.25)] hover:scale-[1.02] active:scale-[0.98]
    `,
  }[variant];

  return (
    <button
      disabled={disabled}
      className={`
        relative inline-flex items-center justify-center font-heading transition-all duration-300
        cursor-pointer select-none disabled:opacity-50 disabled:pointer-events-none disabled:hover:scale-100
        ${sizeClasses}
        ${variantClasses}
        ${className}
      `}
      {...props}
    >
      {/* Specular Inner Glare Highlight */}
      <span className="absolute inset-x-2 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{children}</span>
    </button>
  );
};
