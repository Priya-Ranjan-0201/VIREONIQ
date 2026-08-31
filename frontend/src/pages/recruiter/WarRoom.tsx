import React from 'react';
import { 
  Users, 
  Target, 
  TrendingUp, 
  AlertTriangle,
  Brain,
  ShieldCheck
} from 'lucide-react';

const RecruiterWarRoom = () => {
  const metrics = [
    { label: 'Batch Readiness', value: '84%', icon: Target, color: 'text-blue-500' },
    { label: 'Placement Forecast', value: 'High', icon: TrendingUp, color: 'text-green-500' },
    { label: 'Recruiter Trust', value: '4.8/5', icon: ShieldCheck, color: 'text-purple-500' },
    { label: 'Avg. Readiness', value: '72/100', icon: Brain, color: 'text-orange-500' },
  ];

  const risks = [
    { department: 'Computer Science', risk: 'Low', trend: 'Improving' },
    { department: 'Information Tech', risk: 'Moderate', trend: 'Stable' },
    { department: 'Electronics', risk: 'High', trend: 'Declining' },
  ];

  return (
    <div className="p-8 bg-slate-950 min-h-screen text-white font-outfit">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Recruiter War Room™
          </h1>
          <p className="text-slate-400 mt-2">Enterprise-Grade Institutional Placement Intelligence</p>
        </header>

        {/* Global Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          {metrics.map((m) => (
            <div key={m.label} className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between mb-4">
                <m.icon className={m.color} size={24} />
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Live</span>
              </div>
              <h3 className="text-2xl font-bold">{m.value}</h3>
              <p className="text-slate-500 text-sm">{m.label}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Department Risk Analysis */}
          <div className="bg-slate-900/50 border border-slate-800 p-8 rounded-3xl">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
              <AlertTriangle className="text-orange-500" />
              Institutional Risk Indicators
            </h2>
            <div className="space-y-6">
              {risks.map((r) => (
                <div key={r.department} className="flex items-center justify-between p-4 bg-slate-800/30 rounded-xl">
                  <div>
                    <h4 className="font-bold">{r.department}</h4>
                    <p className="text-xs text-slate-500">Trend: {r.trend}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    r.risk === 'Low' ? 'bg-green-500/20 text-green-400' :
                    r.risk === 'Moderate' ? 'bg-orange-500/20 text-orange-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {r.risk} Risk
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Skill Market Predictor */}
          <div className="bg-slate-900/50 border border-slate-800 p-8 rounded-3xl">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
              <TrendingUp className="text-blue-500" />
              Skill Market Predictor™
            </h2>
            <div className="space-y-4">
              <div className="p-4 border border-blue-500/30 bg-blue-500/5 rounded-xl">
                <h4 className="text-blue-400 font-bold">Hot Skill: Multi-Agent AI Engineering</h4>
                <p className="text-sm text-slate-400 mt-1">Hiring demand expected to spike 300% in next 18 months.</p>
              </div>
              <div className="p-4 border border-purple-500/30 bg-purple-500/5 rounded-xl">
                <h4 className="text-purple-400 font-bold">Trending: Distributed System Observability</h4>
                <p className="text-sm text-slate-400 mt-1">High demand in Tier-1 product companies.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecruiterWarRoom;
