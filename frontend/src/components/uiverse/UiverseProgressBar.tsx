import React from 'react';

interface UiverseProgressBarProps {
  value: number; // 0 to 100
  height?: number; // px, default 8
  showGlow?: boolean;
  showStripes?: boolean;
  animatedStripes?: boolean;
  className?: string;
  variant?: 'cosmic' | 'emerald' | 'sky' | 'peach';
}

export const UiverseProgressBar: React.FC<UiverseProgressBarProps> = ({
  value,
  height = 8,
  showGlow = true,
  showStripes = true,
  animatedStripes = true,
  className = '',
  variant = 'cosmic',
}) => {
  const clampedValue = Math.min(100, Math.max(0, value));

  const gradientClass = {
    cosmic: 'from-[#22c55e] via-[#add8e6] to-[#fdbcb4]',
    emerald: 'from-[#16a34a] via-[#22c55e] to-[#86efac]',
    sky: 'from-[#0284c7] via-[#add8e6] to-[#e0f2fe]',
    peach: 'from-[#f43f5e] via-[#fdbcb4] to-[#fee3de]',
  }[variant];

  const glowColor = {
    cosmic: '#add8e6',
    emerald: '#22c55e',
    sky: '#add8e6',
    peach: '#fdbcb4',
  }[variant];

  return (
    <div className={`relative w-full overflow-hidden rounded-full bg-slate-200/80 dark:bg-white/[0.06] p-[2px] backdrop-blur-sm ${className}`}>
      {/* Outer track border reflection */}
      <div
        className="relative overflow-hidden rounded-full transition-all duration-700 ease-out"
        style={{ height: `${height}px` }}
      >
        {/* Main liquid fill */}
        <div
          className={`h-full rounded-full bg-gradient-to-r ${gradientClass} transition-all duration-700 ease-out relative`}
          style={{
            width: `${clampedValue}%`,
            boxShadow: showGlow ? `0 0 12px ${glowColor}` : 'none',
          }}
        >
          {/* Animated diagonal liquid stripes */}
          {showStripes && (
            <div
              className={`absolute inset-0 opacity-25 ${
                animatedStripes ? 'animate-liquid-stripes' : ''
              }`}
              style={{
                backgroundImage: `
                  linear-gradient(
                    45deg,
                    rgba(255, 255, 255, 0.35) 25%,
                    transparent 25%,
                    transparent 50%,
                    rgba(255, 255, 255, 0.35) 50%,
                    rgba(255, 255, 255, 0.35) 75%,
                    transparent 75%,
                    transparent
                  )
                `,
                backgroundSize: '24px 24px',
              }}
            />
          )}

          {/* Leading-edge glowing orb / bead */}
          {clampedValue > 3 && (
            <div
              className="absolute right-0 top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_8px_#ffffff] animate-ping"
              style={{ transform: 'translate(50%, -50%) scale(0.8)' }}
            />
          )}
        </div>
      </div>
    </div>
  );
};
