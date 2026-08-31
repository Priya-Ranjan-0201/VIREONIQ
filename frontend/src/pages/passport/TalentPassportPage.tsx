import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Award,
  ExternalLink,
  Share2,
  CheckCircle2,
  Lock,
  Layers,
  Sparkles,
  Copy,
  Clock,
  Trash2,
  AlertTriangle,
  Code2,
  ChevronRight,
  TrendingUp
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';
import type { TalentPassportData, VerifiedCompetencyItem } from '@/api/careerIntelligenceApi';

export const TalentPassportPage: React.FC = () => {
  const [targetRole, setTargetRole] = useState<string>('Backend Engineer');
  const [passport, setPassport] = useState<TalentPassportData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showShareModal, setShowShareModal] = useState<boolean>(false);
  const [shareDays, setShareDays] = useState<number>(30);
  const [generatedShare, setGeneratedShare] = useState<any | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [selectedCompetency, setSelectedCompetency] = useState<VerifiedCompetencyItem | null>(null);

  const loadPassport = async () => {
    setLoading(true);
    try {
      const data = await careerIntelligenceApi.getTalentPassport(targetRole);
      setPassport(data);
      if (data.verified_competencies.length > 0) {
        setSelectedCompetency(data.verified_competencies[0]);
      }
    } catch (err) {
      console.error('Failed to load talent passport', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPassport();
  }, [targetRole]);

  const handleCreateShare = async () => {
    try {
      const res = await careerIntelligenceApi.createPassportShareLink(targetRole, undefined, shareDays);
      setGeneratedShare(res);
      await loadPassport();
    } catch (err) {
      console.error('Failed to generate share link', err);
    }
  };

  const handleRevokeShare = async (token: string) => {
    try {
      await careerIntelligenceApi.revokePassportShareLink(token);
      await loadPassport();
    } catch (err) {
      console.error('Failed to revoke share link', err);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(window.location.origin + text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading || !passport) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6">
        <div className="text-center space-y-3">
          <ShieldCheck className="w-10 h-10 text-indigo-400 animate-pulse mx-auto" />
          <p className="text-sm font-mono text-slate-400">Loading Dynamic Talent Passport v6.0.0...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider mb-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              VIREONIQ Trust Registry • Dynamic Talent Passport v6.0.0
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              {passport.candidate.name}'s Talent Passport
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              {passport.candidate.headline} • Independent cryptographic verification layer.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2"
            >
              <option value="Backend Engineer">Role: Backend Engineer</option>
              <option value="Full Stack Engineer">Role: Full Stack Engineer</option>
              <option value="AI/ML Engineer">Role: AI/ML Engineer</option>
            </select>

            <button
              onClick={() => setShowShareModal(true)}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-lg text-sm transition shadow-lg shadow-indigo-500/20"
            >
              <Share2 className="w-4 h-4" />
              Share Passport
            </button>
          </div>
        </div>

        {/* 1. Trust Indicator Hero */}
        <div className="bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900 border border-slate-800 rounded-2xl p-6 lg:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-800 text-emerald-300 font-semibold uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Trust Level: {passport.candidate.trust_indicator}
              </span>
              <span className="text-xs font-mono text-slate-500">Last verified: {passport.last_updated}</span>
            </div>
            <h3 className="text-xl font-bold text-white">
              {passport.role_alignment.alignment_percentage}% Verified Role Alignment
            </h3>
            <p className="text-slate-400 text-sm max-w-2xl">
              {passport.candidate.trust_rationale}
            </p>
          </div>

          <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-xs font-mono space-y-1 shrink-0">
            <div className="text-slate-500">Registry Authority</div>
            <div className="text-slate-200 font-semibold">{passport.verification_registry}</div>
            <div className="text-emerald-400">HMAC-SHA256 Signatures Active</div>
          </div>
        </div>

        {/* 2. Verified Competencies & Provenance Inspector */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Competency List */}
          <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Award className="w-4 h-4 text-indigo-400" />
                Verified Technical Competencies
              </h3>
              <span className="text-xs font-mono text-slate-400">
                {passport.verified_competencies.length} Credentials
              </span>
            </div>

            <div className="space-y-3">
              {passport.verified_competencies.map((comp) => (
                <div
                  key={comp.public_reference}
                  onClick={() => setSelectedCompetency(comp)}
                  className={`p-4 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                    selectedCompetency?.public_reference === comp.public_reference
                      ? 'bg-indigo-950/40 border-indigo-500/50'
                      : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-bold text-white">{comp.competency}</h4>
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-indigo-300">
                        {comp.level}
                      </span>
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-400">
                        ✓ {comp.credential_type.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 font-mono">
                      Ref: {comp.public_reference} • Issued: {comp.issued_at}
                    </div>
                  </div>

                  <ChevronRight className="w-4 h-4 text-slate-500" />
                </div>
              ))}
            </div>
          </div>

          {/* Provenance Drill-Down Inspector */}
          <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Code2 className="w-4 h-4 text-emerald-400" />
              Evidence Provenance Drill-Down
            </h3>

            {selectedCompetency ? (
              <div className="space-y-4 text-xs">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
                  <div>
                    <div className="text-slate-500 font-mono">Competency</div>
                    <div className="text-sm font-bold text-white mt-0.5">{selectedCompetency.competency}</div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80">
                    <div>
                      <div className="text-slate-500 font-mono">Assessment Score</div>
                      <div className="text-emerald-400 font-bold text-base mt-0.5">
                        {selectedCompetency.provenance_drilldown.assessment_score}%
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-500 font-mono">Integrity Status</div>
                      <div className="text-slate-200 font-semibold mt-0.5">
                        {selectedCompetency.provenance_drilldown.integrity_indicator}
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-800/80">
                    <div className="text-slate-500 font-mono">Cryptographic Verification</div>
                    <a
                      href={`/verify/${selectedCompetency.public_reference}`}
                      target="_blank"
                      rel="noreferrer"
                      className="text-indigo-400 hover:text-indigo-300 font-mono flex items-center gap-1 mt-1 underline"
                    >
                      Verify {selectedCompetency.public_reference} <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>

                <div className="text-slate-400 leading-relaxed">
                  Verified through controlled technical assessments and sandbox telemetry with tamper-proof HMAC verification.
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500">Select a competency to inspect verification lineage.</p>
            )}
          </div>
        </div>

        {/* 3. Verified Projects */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
            <Layers className="w-4 h-4 text-indigo-400" />
            Demonstrated Project Evidence
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {passport.demonstrated_projects.map((proj) => (
              <div key={proj.id} className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-white">{proj.project_name}</h4>
                  <span className="text-xs font-mono text-emerald-400">Score: {proj.complexity_score}</span>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {proj.technologies.map((tech) => (
                    <span key={tech} className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                      {tech}
                    </span>
                  ))}
                </div>
                <div className="text-[11px] text-slate-500 font-mono pt-1">
                  Status: {proj.verification_status} • Role Relevance: {proj.role_relevance}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Share Modal */}
        {showShareModal && (
          <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-6 shadow-2xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Share2 className="w-5 h-5 text-indigo-400" />
                  Share Dynamic Talent Passport
                </h3>
                <button onClick={() => setShowShareModal(false)} className="text-slate-400 hover:text-white">✕</button>
              </div>

              <div className="space-y-4">
                <p className="text-xs text-slate-300">
                  Generate a privacy-minimized public link for recruiters. Confidential career gaps, raw transcripts, and private goals will remain strictly hidden.
                </p>

                <div className="space-y-2">
                  <label className="text-xs font-mono text-slate-400">Link Duration</label>
                  <select
                    value={shareDays}
                    onChange={(e) => setShareDays(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded-lg p-2.5"
                  >
                    <option value={7}>7 Days</option>
                    <option value={30}>30 Days (Standard)</option>
                    <option value={90}>90 Days</option>
                    <option value={0}>Permanent (Until Revoked)</option>
                  </select>
                </div>

                <button
                  onClick={handleCreateShare}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg text-xs transition"
                >
                  Generate Share Link
                </button>

                {generatedShare && (
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-2">
                    <div className="text-[11px] text-slate-400 font-mono">Public Share URL</div>
                    <div className="flex items-center gap-2">
                      <input
                        readOnly
                        value={window.location.origin + generatedShare.share_url}
                        className="bg-slate-900 border border-slate-800 text-xs font-mono text-slate-200 p-2 rounded-lg flex-1"
                      />
                      <button
                        onClick={() => copyToClipboard(generatedShare.share_url)}
                        className="bg-slate-800 hover:bg-slate-700 p-2 rounded-lg text-slate-200"
                      >
                        {copied ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                )}

                {/* Active Shares List */}
                {passport.active_share_links && passport.active_share_links.length > 0 && (
                  <div className="pt-2 border-t border-slate-800 space-y-2">
                    <div className="text-xs font-bold text-white">Active Share Links</div>
                    <div className="space-y-2 max-h-36 overflow-y-auto">
                      {passport.active_share_links.map((link) => (
                        <div key={link.share_token} className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 flex items-center justify-between text-xs font-mono">
                          <div>
                            <div className="text-slate-300">{link.share_token.slice(0, 16)}...</div>
                            <div className="text-[10px] text-slate-500">{link.view_count} views</div>
                          </div>
                          <button
                            onClick={() => handleRevokeShare(link.share_token)}
                            className="text-red-400 hover:text-red-300 p-1.5"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
