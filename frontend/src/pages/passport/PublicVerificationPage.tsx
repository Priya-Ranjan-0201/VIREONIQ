import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Award,
  Lock,
  ExternalLink,
  Search,
  Calendar,
  Compass
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';
import type { PublicVerificationResult } from '@/api/careerIntelligenceApi';

export const PublicVerificationPage: React.FC = () => {
  const { reference } = useParams<{ reference?: string }>();
  const [queryRef, setQueryRef] = useState<string>(reference || 'VX-PY-8F31B2A4');
  const [result, setResult] = useState<PublicVerificationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async (refToVerify: string) => {
    if (!refToVerify.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await careerIntelligenceApi.verifyPublicCredential(refToVerify.trim());
      setResult(data);
    } catch (err: any) {
      console.error('Verification failed', err);
      setError('Unable to verify credential. Reference may not exist in the Trust Registry.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (reference) {
      setQueryRef(reference);
      handleVerify(reference);
    }
  }, [reference]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6">
      <div className="max-w-2xl w-full space-y-8">
        {/* Registry Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/80 border border-indigo-800 text-indigo-300 text-xs font-mono uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            VIREONIQ Trust Registry
          </div>
          <h1 className="text-3xl font-bold text-white">
            Credential Verification Portal
          </h1>
          <p className="text-slate-400 text-xs max-w-md mx-auto">
            Independently verify competency authenticity, cryptographic signatures, and evidence provenance.
          </p>
        </div>

        {/* Verification Lookup Bar */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex items-center gap-3 shadow-xl">
          <Search className="w-5 h-5 text-slate-500 shrink-0 ml-2" />
          <input
            type="text"
            value={queryRef}
            onChange={(e) => setQueryRef(e.target.value)}
            placeholder="Enter Credential Reference (e.g. VX-PY-8F31B2A4)"
            className="bg-transparent border-none text-slate-100 text-sm font-mono focus:outline-none flex-1"
          />
          <button
            onClick={() => handleVerify(queryRef)}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-xl text-xs transition"
          >
            {loading ? 'Verifying...' : 'Verify Reference'}
          </button>
        </div>

        {/* Verification Result Card */}
        {result && (
          <div className={`border rounded-2xl p-6 lg:p-8 space-y-6 shadow-2xl transition ${
            result.valid
              ? 'bg-slate-900/90 border-emerald-500/40 shadow-emerald-950/10'
              : 'bg-slate-900/90 border-red-500/40 shadow-red-950/10'
          }`}>
            {/* Status Banner */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                {result.valid ? (
                  <div className="w-10 h-10 rounded-full bg-emerald-950 border border-emerald-700 flex items-center justify-center text-emerald-400">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                ) : (
                  <div className="w-10 h-10 rounded-full bg-red-950 border border-red-700 flex items-center justify-center text-red-400">
                    <XCircle className="w-6 h-6" />
                  </div>
                )}
                <div>
                  <div className="text-xs font-mono uppercase text-slate-400">Verification Status</div>
                  <h3 className={`text-lg font-bold ${result.valid ? 'text-emerald-400' : 'text-red-400'}`}>
                    {result.valid ? 'AUTHENTIC & ACTIVE' : result.credential?.status || 'INVALID / NOT FOUND'}
                  </h3>
                </div>
              </div>

              <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-slate-400">
                {result.verification?.signature_status || 'UNVERIFIED'}
              </span>
            </div>

            {/* Credential Details (Privacy Minimized) */}
            {result.credential && (
              <div className="space-y-4 text-xs font-mono">
                <div className="grid grid-cols-2 gap-4 bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                  <div>
                    <span className="text-slate-500">Competency</span>
                    <div className="text-sm font-bold text-white mt-1">{result.credential.competency}</div>
                  </div>
                  <div>
                    <span className="text-slate-500">Demonstrated Level</span>
                    <div className="text-sm font-bold text-indigo-300 mt-1">{result.credential.level}</div>
                  </div>
                  <div>
                    <span className="text-slate-500">Issuer Authority</span>
                    <div className="text-slate-200 mt-1">{result.credential.issuer}</div>
                  </div>
                  <div>
                    <span className="text-slate-500">Public Reference</span>
                    <div className="text-slate-200 mt-1">{result.credential.public_reference}</div>
                  </div>
                </div>

                <div className="space-y-1 bg-slate-950/50 p-3 rounded-xl border border-slate-800/80 text-slate-300">
                  <div className="text-slate-500">Evidence Provenance:</div>
                  <div>{result.credential.evidence_proof}</div>
                  <div className="text-[11px] text-slate-500 mt-1">Verified on: {result.credential.verified_at || result.credential.issued_at}</div>
                </div>
              </div>
            )}

            {/* Cryptographic Footer */}
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 border-t border-slate-800/80 pt-4">
              <span className="flex items-center gap-1">
                <Lock className="w-3 h-3 text-emerald-400" /> HMAC-SHA256 Cryptographic Registry
              </span>
              <span>Checked: {result.verification?.checked_at ? new Date(result.verification.checked_at).toLocaleTimeString() : 'Now'}</span>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-950/40 border border-red-800/60 p-4 rounded-xl text-xs text-red-300 text-center font-mono">
            {error}
          </div>
        )}

        {/* Back Link */}
        <div className="text-center">
          <Link to="/app/talent-passport" className="text-xs text-slate-500 hover:text-slate-300 font-mono transition">
            ← Return to Candidate Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};
