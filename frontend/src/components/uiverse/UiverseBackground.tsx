import React from 'react';

interface UiverseBackgroundProps {
  className?: string;
  showGrid?: boolean;
}

export const UiverseBackground: React.FC<UiverseBackgroundProps> = ({
  className = '',
  showGrid = true,
}) => {
  return (
    <div className={`pointer-events-none fixed inset-0 z-0 overflow-hidden ${className}`}>
      {/* Subtle Precision Geometric Grid */}
      {showGrid && (
        <div
          className="absolute inset-0 opacity-[0.035] dark:opacity-[0.04]"
          style={{
            backgroundImage: `
              linear-gradient(to right, currentColor 1px, transparent 1px),
              linear-gradient(to bottom, currentColor 1px, transparent 1px)
            `,
            backgroundSize: '54px 54px',
          }}
        />
      )}
    </div>
  );
};
