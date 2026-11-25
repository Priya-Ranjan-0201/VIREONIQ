import React from 'react';

interface UiverseScannerProps {
  label?: string;
  isScanning?: boolean;
  score?: number;
  className?: string;
}

export const UiverseScanner: React.FC<UiverseScannerProps> = ({
  label = 'AI Neural Diagnostics Active',
  isScanning = true,
  score,
  className = '',
}) => {
  return (
    <div className={`relative overflow-hidden rounded-2xl border border-slate-200/90 dark:border-white/10 bg-slate-900/90 dark:bg-[#0e1428]/95 p-6 backdrop-blur-2xl shadow-xl ${className}`}>
      {/* Background Cyber Grid */}
      <div
        className="pointer-events-none absolute inset-0 opacity-15"
        style={{
          backgroundImage: `
            linear-gradient(to right, #add8e6 1px, transparent 1px),
            linear-gradient(to bottom, #add8e6 1px, transparent 1px)
          `,
          backgroundSize: '24px 24px',
        }}
      />

      {/* Sweeping Laser Beam Animation */}
      {isScanning && (
        <div className="pointer-events-none absolute inset-x-0 h-2 bg-gradient-to-r from-transparent via-[#add8e6] to-transparent opacity-75 shadow-[0_0_20px_#add8e6] animate-scanner-beam" />
      )}

      {/* Crosshair Corner Brackets */}
      <div className="pointer-events-none absolute top-2 left-2 w-3 h-3 border-t-2 border-l-2 border-[#add8e6]/70" />
      <div className="pointer-events-none absolute top-2 right-2 w-3 h-3 border-t-2 border-r-2 border-[#fdbcb4]/70" />
      <div className="pointer-events-none absolute bottom-2 left-2 w-3 h-3 border-b-2 border-l-2 border-[#22c55e]/70" />
      <div className="pointer-events-none absolute bottom-2 right-2 w-3 h-3 border-b-2 border-r-2 border-white/70" />

      {/* Content Area */}
      <div className="relative z-10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          {/* Animated Sonar Radar Core */}
          <div className="relative flex items-center justify-center w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700/80">
            <span className="w-2.5 h-2.5 rounded-full bg-[#22c55e] shadow-[0_0_12px_#22c55e]" />
            <span className="absolute w-7 h-7 rounded-full border border-[#add8e6]/40 animate-ping" />
            <span className="absolute w-10 h-10 rounded-full border border-[#fdbcb4]/30 animate-pulse" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#22c55e] animate-ping" />
              <span className="text-xs font-bold uppercase tracking-wider text-[#add8e6]">
                {label}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              Continuously benchmarking ATS keywords, STAR metrics & evidence graph integrity
            </p>
          </div>
        </div>

        {typeof score === 'number' && (
          <div className="flex items-center gap-3 bg-white/5 border border-white/10 px-4 py-2 rounded-xl backdrop-blur-md shrink-0">
            <div className="text-right">
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Match Index</span>
              <p className="text-2xl font-black text-white font-heading">{score}%</p>
            </div>
            <div className="w-9 h-9 rounded-lg bg-[#22c55e]/20 border border-[#22c55e]/40 flex items-center justify-center text-[#22c55e]">
              ✓
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
