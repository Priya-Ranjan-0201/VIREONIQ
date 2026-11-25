import React from 'react';
import { UiverseMotionCanvas } from './UiverseMotionCanvas';

interface UiverseBackgroundProps {
  className?: string;
  showGrid?: boolean;
  showParticles?: boolean;
}

export const UiverseBackground: React.FC<UiverseBackgroundProps> = ({
  className = '',
  showGrid = true,
  showParticles = true,
}) => {
  return (
    <div className={`pointer-events-none fixed inset-0 z-0 overflow-hidden ${className}`}>
      {/* Dynamic Aurora Lighting Orbs using User's Exact Palette */}
      {/* 1. Coral Peach (#fdbcb4) Bloom */}
      <div className="absolute -top-[20%] left-[15%] h-[700px] w-[700px] rounded-full bg-[#fdbcb4]/25 dark:bg-[#fdbcb4]/18 blur-[140px] animate-aurora-1" />

      {/* 2. Powder Sky Blue (#add8e6) Bloom */}
      <div className="absolute top-[25%] -right-[10%] h-[750px] w-[750px] rounded-full bg-[#add8e6]/30 dark:bg-[#add8e6]/18 blur-[150px] animate-aurora-2" />

      {/* 3. Emerald Green (#22c55e) Bloom */}
      <div className="absolute -bottom-[20%] left-[30%] h-[650px] w-[650px] rounded-full bg-[#22c55e]/20 dark:bg-[#22c55e]/15 blur-[150px] animate-aurora-3" />

      {/* 4. White / Subtle Light Bloom */}
      <div className="absolute top-[10%] -left-[10%] h-[500px] w-[500px] rounded-full bg-white/40 dark:bg-white/[0.05] blur-[130px] animate-pulse-glow" />

      {/* Subtle Geometric Cyber Grid */}
      {showGrid && (
        <div
          className="absolute inset-0 opacity-[0.03] dark:opacity-[0.04]"
          style={{
            backgroundImage: `
              linear-gradient(to right, currentColor 1px, transparent 1px),
              linear-gradient(to bottom, currentColor 1px, transparent 1px)
            `,
            backgroundSize: '54px 54px',
          }}
        />
      )}

      {/* 60fps Floating Constellation Motion Graphic Canvas */}
      {showParticles && (
        <UiverseMotionCanvas particleCount={36} speed={0.45} interactive={true} />
      )}
    </div>
  );
};
