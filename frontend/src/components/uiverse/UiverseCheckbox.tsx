import React from 'react';
import { Check } from 'lucide-react';

interface UiverseCheckboxProps {
  id?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: React.ReactNode;
  color?: 'emerald' | 'sky' | 'peach';
  disabled?: boolean;
}

export const UiverseCheckbox: React.FC<UiverseCheckboxProps> = ({
  id,
  checked,
  onChange,
  label,
  color = 'emerald',
  disabled = false,
}) => {
  const colorStyles = {
    emerald: {
      activeBg: 'bg-[#22c55e] border-[#22c55e] text-white shadow-[0_0_12px_rgba(34,197,94,0.5)]',
      glow: 'shadow-[0_0_14px_rgba(34,197,94,0.4)]',
    },
    sky: {
      activeBg: 'bg-[#add8e6] border-[#add8e6] text-slate-950 shadow-[0_0_12px_rgba(173,216,230,0.5)]',
      glow: 'shadow-[0_0_14px_rgba(173,216,230,0.4)]',
    },
    peach: {
      activeBg: 'bg-[#fdbcb4] border-[#fdbcb4] text-slate-950 shadow-[0_0_12px_rgba(253,188,180,0.5)]',
      glow: 'shadow-[0_0_14px_rgba(253,188,180,0.4)]',
    },
  }[color];

  return (
    <label
      htmlFor={id}
      className={`
        inline-flex items-center gap-2.5 cursor-pointer select-none text-xs group
        ${disabled ? 'opacity-50 pointer-events-none' : ''}
      `}
    >
      <div className="relative">
        <input
          type="checkbox"
          id={id}
          checked={checked}
          disabled={disabled}
          onChange={(e) => onChange(e.target.checked)}
          className="sr-only"
        />
        {/* Animated Uiverse Jelly Checkbox Box */}
        <div
          className={`
            w-5 h-5 rounded-lg border-2 transition-all duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]
            flex items-center justify-center
            ${
              checked
                ? `${colorStyles.activeBg} scale-105`
                : 'bg-white/50 dark:bg-slate-900/60 border-slate-300 dark:border-white/20 group-hover:border-slate-400 dark:group-hover:border-white/40'
            }
          `}
        >
          <Check
            className={`
              w-3.5 h-3.5 stroke-[3] transition-all duration-300 ease-out
              ${checked ? 'scale-100 opacity-100' : 'scale-0 opacity-0'}
            `}
          />
        </div>
      </div>
      {label && (
        <span className="text-slate-600 dark:text-slate-300 font-medium group-hover:text-slate-900 dark:group-hover:text-white transition-colors">
          {label}
        </span>
      )}
    </label>
  );
};
