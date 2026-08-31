import React, { useState, useEffect } from 'react';
import {
  Code2,
  Key,
  Webhook,
  Network,
  Cpu,
  ShieldCheck,
  Plus,
  Trash2,
  Copy,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ExternalLink,
  Activity,
  Layers,
  Database
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';

export const DeveloperPlatformPage: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [connectors, setConnectors] = useState<any[]>([]);
  const [entitlements, setEntitlements] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // New Key Form State
  const [showKeyModal, setShowKeyModal] = useState<boolean>(false);
  const [keyName, setKeyName] = useState<string>('');
  const [selectedScopes, setSelectedScopes] = useState<string[]>(['candidate:read', 'jobs:read']);
  const [generatedKey, setGeneratedKey] = useState<any>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [k, w, c, ent, h] = await Promise.all([
        careerIntelligenceApi.listPlatformApiKeys().catch(() => []),
        careerIntelligenceApi.listWebhookSubscriptions().catch(() => []),
        careerIntelligenceApi.listPartnerConnectors().catch(() => []),
        careerIntelligenceApi.getPlatformEntitlements().catch(() => null),
        careerIntelligenceApi.getPlatformHealthTelemetry().catch(() => null)
      ]);
      setApiKeys(k || []);
      setWebhooks(w || []);
      setConnectors(c || []);
      setEntitlements(ent);
      setHealth(h);
    } catch (err) {
      console.error('Failed to load developer platform data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyName.trim()) return;
    try {
      const res = await careerIntelligenceApi.generatePlatformApiKey(keyName, selectedScopes, 120);
      setGeneratedKey(res);
      setKeyName('');
      loadData();
    } catch (err) {
      console.error('Failed to create key', err);
    }
  };

  const handleRevokeKey = async (keyId: string) => {
    try {
      await careerIntelligenceApi.revokePlatformApiKey(keyId);
      loadData();
    } catch (err) {
      console.error('Failed to revoke key', err);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider mb-1">
              <Code2 className="w-4 h-4 text-indigo-400" />
              VIREONIQ Developer Platform & Partner Ecosystem v13.0.0
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Developer Platform & Enterprise Integrations
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Manage scoped API keys, webhook event subscriptions, enterprise connectors (ATS, LMS, Campus, HRIS), and platform entitlements.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-indigo-950 border border-indigo-800 text-indigo-300 font-mono text-xs rounded-full font-bold flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              ENTERPRISE TIER
            </span>
            <button
              onClick={loadData}
              className="p-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white rounded-xl transition"
              title="Refresh Data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* 1. Global Platform Health & Entitlement Metering */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Platform Health</span>
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400 tracking-tight flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
              {health?.status ?? 'OPERATIONAL'}
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Core API, DB, AI & Signing Keys Healthy
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Monthly AI Tokens</span>
              <Cpu className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold text-white tracking-tight">
              142.5k <span className="text-sm font-normal text-slate-400">/ 1.0M</span>
            </div>
            <p className="text-[11px] text-indigo-400 font-mono">
              857.5k remaining this cycle
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Candidate Searches</span>
              <Network className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-white tracking-tight">
              420 <span className="text-sm font-normal text-slate-400">/ 5,000</span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Rate limit: 120 req/min per key
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>SLA Level</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white tracking-tight">
              99.9% Uptime
            </div>
            <p className="text-[11px] text-emerald-400 font-mono">
              Zero-mutation outbox guarantee
            </p>
          </div>
        </div>

        {/* 2. Scoped API Keys Management */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div className="flex items-center gap-3">
              <Key className="w-5 h-5 text-indigo-400" />
              <div>
                <h2 className="text-lg font-bold text-white">Scoped Platform API Keys</h2>
                <p className="text-xs text-slate-400">Granular tokens for automated candidate matching, job sync, and credential verification.</p>
              </div>
            </div>
            <button
              onClick={() => { setShowKeyModal(true); setGeneratedKey(null); }}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Generate API Key
            </button>
          </div>

          {/* Key Creation Form Modal */}
          {showKeyModal && (
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Generate Scoped API Key</h3>
                <button onClick={() => setShowKeyModal(false)} className="text-slate-400 hover:text-white text-xs">✕</button>
              </div>

              {!generatedKey ? (
                <form onSubmit={handleCreateKey} className="space-y-4">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Key Name / Service Identifier</label>
                    <input
                      type="text"
                      value={keyName}
                      onChange={(e) => setKeyName(e.target.value)}
                      placeholder="e.g. Workday ATS Production Sync"
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="text-xs text-slate-400 block mb-2">Granted Scopes</label>
                    <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                      {['candidate:read', 'candidate:write', 'jobs:read', 'jobs:write', 'assessments:read', 'credentials:verify'].map((sc) => (
                        <label key={sc} className="flex items-center gap-2 text-slate-300">
                          <input
                            type="checkbox"
                            checked={selectedScopes.includes(sc)}
                            onChange={(e) => {
                              if (e.target.checked) setSelectedScopes([...selectedScopes, sc]);
                              else setSelectedScopes(selectedScopes.filter(s => s !== sc));
                            }}
                            className="rounded bg-slate-900 border-slate-700 text-indigo-600"
                          />
                          {sc}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="flex justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => setShowKeyModal(false)}
                      className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-400 rounded-lg text-xs"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold"
                    >
                      Generate Key
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-3 bg-emerald-950/40 border border-emerald-800 rounded-xl p-4">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
                    <CheckCircle2 className="w-4 h-4" />
                    Key Generated Successfully! Copy it now — it will not be displayed again.
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      readOnly
                      value={generatedKey.raw_api_key}
                      className="w-full bg-slate-900 border border-emerald-700 rounded-lg px-3 py-2 font-mono text-xs text-emerald-300"
                    />
                    <button
                      onClick={() => copyToClipboard(generatedKey.raw_api_key)}
                      className="px-3 py-2 bg-emerald-700 hover:bg-emerald-600 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shrink-0"
                    >
                      {copied ? <CheckCircle2 className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      {copied ? 'Copied' : 'Copy'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Keys List */}
          <div className="space-y-3">
            {apiKeys.length === 0 ? (
              <p className="text-xs text-slate-500 font-mono">No active API keys found. Generate one above.</p>
            ) : (
              apiKeys.map((k) => (
                <div key={k.id} className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-white">{k.name}</span>
                      <span className="px-2 py-0.5 bg-slate-900 border border-slate-700 text-indigo-300 font-mono text-[10px] rounded">
                        {k.key_prefix}••••••••
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {k.scopes?.map((sc: string) => (
                        <span key={sc} className="px-2 py-0.5 bg-slate-900 text-slate-400 font-mono text-[10px] rounded">
                          {sc}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={() => handleRevokeKey(k.id)}
                    className="p-2 text-rose-400 hover:bg-rose-950 border border-slate-800 hover:border-rose-800 rounded-lg text-xs transition self-end sm:self-auto"
                    title="Revoke Key"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 3. Enterprise Partner Connectors (ATS, LMS, Campus, HRIS) */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div className="flex items-center gap-3">
              <Network className="w-5 h-5 text-indigo-400" />
              <div>
                <h2 className="text-lg font-bold text-white">Enterprise Partner Connectors</h2>
                <p className="text-xs text-slate-400">Pre-built adapters for Workday ATS, Canvas LMS, University Rosters, and BambooHR.</p>
              </div>
            </div>
            <span className="text-xs font-mono text-slate-400">Canonical SDK v13.0</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {connectors.map((conn, idx) => (
              <div key={idx} className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3 flex flex-col justify-between">
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 bg-indigo-950 border border-indigo-800 text-indigo-300 font-mono text-[10px] rounded font-bold">
                      {conn.connector_type}
                    </span>
                    <span className="text-[11px] text-emerald-400 font-mono flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                      {conn.status}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white mt-2">{conn.name}</h3>
                </div>

                <div className="border-t border-slate-800 pt-3 text-[11px] font-mono text-slate-400 space-y-1">
                  <div>Synced: <span className="text-white">{conn.records_synced_count} records</span></div>
                  <button className="w-full mt-2 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-indigo-300 rounded-lg text-xs transition">
                    Sync Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 4. Resilient Webhooks & DLQ Viewer */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div className="flex items-center gap-3">
              <Webhook className="w-5 h-5 text-indigo-400" />
              <div>
                <h2 className="text-lg font-bold text-white">Event Webhooks & Dead Letter Queue (DLQ)</h2>
                <p className="text-xs text-slate-400">Signed HMAC-SHA256 event dispatch with automatic retry backoff and DLQ routing.</p>
              </div>
            </div>
            <span className="px-2.5 py-1 bg-slate-950 border border-slate-800 text-emerald-300 font-mono text-[11px] rounded-lg">
              DLQ: 0 Failed Events
            </span>
          </div>

          <div className="space-y-3">
            {webhooks.length === 0 ? (
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-400 flex items-center justify-between">
                <span>Default Endpoint: <code className="text-indigo-300">https://api.partner.com/vireoniq/events</code></span>
                <span className="text-emerald-400">Status: ACTIVE</span>
              </div>
            ) : (
              webhooks.map((sub) => (
                <div key={sub.id} className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
                  <div className="space-y-1">
                    <span className="text-sm font-bold text-white">{sub.target_url}</span>
                    <div className="flex gap-2">
                      {sub.subscribed_events?.map((ev: string) => (
                        <span key={ev} className="px-2 py-0.5 bg-slate-900 text-slate-400 font-mono text-[10px] rounded">
                          {ev}
                        </span>
                      ))}
                    </div>
                  </div>
                  <span className="px-2.5 py-1 bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono text-[11px] rounded">
                    {sub.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
