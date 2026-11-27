import { Brain, Cpu, Dna, Shield, Star, Target, TrendingUp, Zap } from 'lucide-react';
import { useState } from 'react';
import { PreviewBanner, SampleDataBadge } from '@/components/shared/SampleDataBanner';

const TRAIT_LABELS = [
  { key: 'Technical Precision', icon: Cpu, color: '#6366F1', desc: 'Accuracy & depth in technical answers' },
  { key: 'Pressure Tolerance', icon: Shield, color: '#06B6D4', desc: 'Performance under time & stress' },
  { key: 'Communication Clarity', icon: Star, color: '#10B981', desc: 'Articulation & structured thinking' },
  { key: 'Problem Decomposition', icon: Target, color: '#F59E0B', desc: 'Breaking down complex problems' },
  { key: 'Debugging Persistence', icon: Zap, color: '#EF4444', desc: 'Resilience through hard problems' },
  { key: 'Feedback Adaptability', icon: TrendingUp, color: '#8B5CF6', desc: 'Learning from corrections' },
  { key: 'Architectural Rigor', icon: Brain, color: '#EC4899', desc: 'System design & scalability depth' },
  { key: 'Business & Product Acumen', icon: Star, color: '#14B8A6', desc: 'Product thinking & business sense' },
];

type TraitKey = 'Technical Precision' | 'Pressure Tolerance' | 'Communication Clarity' | 'Problem Decomposition' | 'Debugging Persistence' | 'Feedback Adaptability' | 'Architectural Rigor' | 'Business & Product Acumen';

const MOCK_DNA = {
  profile_type_label: 'The Pragmatic Debugger (Sample Archetype)',
  traits: {
    'Technical Precision': 0.82,
    'Pressure Tolerance': 0.71,
    'Communication Clarity': 0.65,
    'Problem Decomposition': 0.78,
    'Debugging Persistence': 0.88,
    'Feedback Adaptability': 0.70,
    'Architectural Rigor': 0.60,
    'Business & Product Acumen': 0.55,
  } as Record<TraitKey, number>,
  alignment_heuristics: { 'Technical Consulting': 82, 'Early-Stage Startup': 78, 'Core Product Engineering': 72, 'Enterprise Platform': 64 },
};

export const PsychometricDNAPage = () => {
  const [data] = useState(MOCK_DNA);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <div className="flex items-center gap-3 mb-1">
          <h2 className="text-3xl font-bold text-slate-50 flex items-center gap-3">
            <Dna className="w-8 h-8 text-cyan-400" /> Psychometric Reflection DNA
          </h2>
          <SampleDataBadge label="Experimental Archetype Demo" />
        </div>
        <p className="text-slate-400 mt-2">
          Self-reflection framework modeling stylistic technical habits and problem-solving patterns.
        </p>
      </header>

      <PreviewBanner
        title="Experimental Behavioral Archetype Preview"
        description="This profile is an illustrative demonstration for candidate self-reflection. It is NOT an accredited psychological test, hiring decision filter, or statistically calibrated predictor of employment outcomes."
        tier="Tier 3 Review Gated"
      />

      {/* Profile Archetype */}
      <div className="bg-gradient-to-r from-purple-600/20 to-cyan-600/20 border border-purple-500/30 rounded-3xl p-8 text-center">
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-3">Self-Reflection Archetype</p>
        <h3 className="text-3xl font-black text-white">{data.profile_type_label}</h3>
        <p className="text-slate-400 mt-2 text-sm">Demonstration showing simulated trait balances across technical exercise samples</p>
      </div>

      {/* Trait Bars */}
      <div className="bg-slate-950 border border-white/10 rounded-3xl p-8">
        <h3 className="text-lg font-bold text-slate-50 mb-6">Trait Dimension Spectrum (Illustrative)</h3>
        <div className="space-y-5">
          {TRAIT_LABELS.map((t) => (
            <div key={t.key}>
              <div className="flex justify-between mb-2">
                <div className="flex items-center gap-2">
                  <t.icon className="w-4 h-4" style={{ color: t.color }} />
                  <span className="text-sm font-medium text-slate-300">{t.key}</span>
                </div>
                <span className="text-sm font-black text-slate-100">
                  {Math.round((data.traits[t.key as TraitKey] || 0) * 100)}%
                </span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-1000"
                  style={{ width: `${(data.traits[t.key as TraitKey] || 0) * 100}%`, background: t.color }}
                />
              </div>
              <p className="text-[10px] text-slate-600 mt-1">{t.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Alignment Matrix */}
      <div className="bg-slate-950 border border-white/10 rounded-3xl p-8">
        <h3 className="text-lg font-bold text-slate-50 mb-4">Workplace Alignment Estimate (Heuristic Sample)</h3>
        <p className="text-xs text-slate-500 mb-6">
          Estimates describe potential working-style compatibility with team environments based on self-reported preferences.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(data.alignment_heuristics).map(([category, score]) => (
            <div key={category} className="p-4 rounded-2xl bg-white/5 border border-white/10">
              <p className="text-[10px] text-slate-400 font-bold uppercase">{category}</p>
              <p className="text-2xl font-black text-cyan-400 mt-1">{score}%</p>
              <p className="text-[10px] text-slate-500 mt-1">Sample heuristic match</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
