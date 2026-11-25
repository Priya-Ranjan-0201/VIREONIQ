import React from 'react';

interface UiverseAudioVisualizerProps {
  isActive?: boolean;
  barCount?: number;
  className?: string;
}

export const UiverseAudioVisualizer: React.FC<UiverseAudioVisualizerProps> = ({
  isActive = true,
  barCount = 18,
  className = '',
}) => {
  // Preset animation heights and delays for smooth organic soundwave motion
  const barConfigs = [
    { height: 'h-4', delay: '0.1s', color: '#fdbcb4' },
    { height: 'h-7', delay: '0.25s', color: '#fdbcb4' },
    { height: 'h-10', delay: '0.05s', color: '#add8e6' },
    { height: 'h-6', delay: '0.35s', color: '#add8e6' },
    { height: 'h-12', delay: '0.15s', color: '#22c55e' },
    { height: 'h-8', delay: '0.4s', color: '#22c55e' },
    { height: 'h-5', delay: '0.2s', color: '#add8e6' },
    { height: 'h-11', delay: '0.3s', color: '#fdbcb4' },
    { height: 'h-7', delay: '0.1s', color: '#add8e6' },
    { height: 'h-12', delay: '0.2s', color: '#22c55e' },
    { height: 'h-9', delay: '0.4s', color: '#add8e6' },
    { height: 'h-6', delay: '0.15s', color: '#fdbcb4' },
    { height: 'h-10', delay: '0.3s', color: '#22c55e' },
    { height: 'h-8', delay: '0.05s', color: '#add8e6' },
    { height: 'h-5', delay: '0.25s', color: '#fdbcb4' },
    { height: 'h-9', delay: '0.35s', color: '#22c55e' },
    { height: 'h-6', delay: '0.1s', color: '#add8e6' },
    { height: 'h-4', delay: '0.2s', color: '#fdbcb4' },
  ];

  return (
    <div className={`flex items-center justify-center gap-1 h-14 px-4 py-2 rounded-2xl bg-slate-900/40 dark:bg-black/30 border border-slate-200/50 dark:border-white/10 backdrop-blur-xl ${className}`}>
      {barConfigs.slice(0, barCount).map((bar, i) => (
        <span
          key={i}
          className={`w-1 rounded-full transition-all duration-300 ${
            isActive ? `${bar.height} animate-sound-wave` : 'h-3 animate-sound-wave opacity-60'
          }`}
          style={{
            backgroundColor: bar.color,
            boxShadow: `0 0 6px ${bar.color}`,
            animationDelay: bar.delay,
            animationDuration: isActive ? '1.2s' : '2.4s',
          }}
        />
      ))}
    </div>
  );
};
