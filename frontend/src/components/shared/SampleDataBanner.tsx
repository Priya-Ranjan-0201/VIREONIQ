import React from 'react';
import { AlertCircle, Eye } from 'lucide-react';

interface SampleDataBadgeProps {
  label?: string;
  className?: string;
}

export const SampleDataBadge: React.FC<SampleDataBadgeProps> = ({
  label = "Sample / Preview Data",
  className = "",
}) => {
  return (
    <span
      data-testid="sample-data-badge"
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-amber-500/10 text-amber-500 border border-amber-500/30 ${className}`}
    >
      <Eye className="w-3 h-3 text-amber-500 shrink-0" />
      <span>{label}</span>
    </span>
  );
};

interface PreviewBannerProps {
  title?: string;
  description?: string;
  tier?: string;
  className?: string;
}

export const PreviewBanner: React.FC<PreviewBannerProps> = ({
  title = "Demonstration Preview",
  description = "This view displays synthetic demonstration data. Real calculations require verified session history and live telemetry connection.",
  tier = "Preview Only",
  className = "",
}) => {
  return (
    <div
      data-testid="preview-banner"
      className={`rounded-2xl border border-amber-500/30 bg-amber-500/5 p-4 mb-6 flex items-start gap-3 text-amber-300 ${className}`}
    >
      <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <p className="font-semibold text-sm text-amber-200">{title}</p>
          <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
            {tier}
          </span>
        </div>
        <p className="text-xs text-amber-300/80 leading-relaxed">{description}</p>
      </div>
    </div>
  );
};

export const TrademarkDisclaimer: React.FC<{ className?: string }> = ({ className = "" }) => {
  return (
    <div data-testid="trademark-disclaimer" className={`p-3 rounded-xl border border-slate-800 bg-slate-950/60 text-[11px] text-slate-400 leading-relaxed ${className}`}>
      <span className="font-semibold text-slate-300">Trademark Notice: </span>
      All company names, logos, and brands cited on this platform are trademarks or registered trademarks of their respective owners. Mention is strictly for independent educational preparation, curriculum mapping, and interview simulation. VIREONIQ is not affiliated with, sponsored by, or endorsed by any named corporation.
    </div>
  );
};
