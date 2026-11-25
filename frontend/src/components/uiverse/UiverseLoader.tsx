import React from 'react';

interface UiverseLoaderProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

export const UiverseLoader: React.FC<UiverseLoaderProps> = ({
  size = 'md',
  text,
  className = '',
}) => {
  const dimensionClass = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
  }[size];

  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
      {/* 3-Ring Orbital Gyroscopic Uiverse Spinner */}
      <div className={`relative ${dimensionClass}`}>
        {/* Ring 1 - Peach Coral */}
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-[#fdbcb4] animate-spin shadow-[0_0_10px_#fdbcb4]" style={{ animationDuration: '0.8s' }} />
        {/* Ring 2 - Powder Sky Blue */}
        <div className="absolute inset-1 rounded-full border-2 border-transparent border-r-[#add8e6] animate-spin shadow-[0_0_10px_#add8e6]" style={{ animationDirection: 'reverse', animationDuration: '1.2s' }} />
        {/* Ring 3 - Emerald Green */}
        <div className="absolute inset-2 rounded-full border-2 border-transparent border-b-[#22c55e] animate-spin shadow-[0_0_10px_#22c55e]" style={{ animationDuration: '1.6s' }} />
      </div>
      {text && (
        <p className="text-xs font-semibold tracking-wider font-heading text-slate-600 dark:text-slate-300 animate-pulse">
          {text}
        </p>
      )}
    </div>
  );
};
