import React, { useState, useEffect } from 'react';
import { ShieldCheck, PhoneCall, Trash2, Send, Clock, ToggleLeft, ToggleRight, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/axios';

interface ParentConnection {
  id: string;
  parent_name: string;
  parent_phone: string;
  consent_status: string; // pending | active | revoked | delivery_failed
  consent_requested_at: string;
  consented_at: string | null;
}

export const ParentConnect = () => {
  const [connections, setConnections] = useState<ParentConnection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  // Form states
  const [parentName, setParentName] = useState('');
  const [parentPhone, setParentPhone] = useState('');

  useEffect(() => {
    fetchConnections();
  }, []);

  const fetchConnections = async () => {
    try {
      const res = await api.get('/parent-link/status');
      setConnections(res.data);
    } catch (e) {
      toast.error('Failed to load parent connection list.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRequestLink = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!parentName.trim() || !parentPhone.trim()) return;

    setSubmitting(true);
    try {
      await api.post('/parent-link/request', {
        parent_name: parentName,
        parent_phone: parentPhone
      });
      toast.success('Connection request created. In-app approval notice sent to your profile!');
      setParentName('');
      setParentPhone('');
      fetchConnections();
    } catch (e) {
      toast.error('Failed to create parent connection.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmConnection = async (id: string) => {
    try {
      await api.post('/parent-link/confirm', { parent_link_id: id });
      toast.success('Parent connection confirmed! Weekly WhatsApp updates active.');
      fetchConnections();
    } catch (e) {
      toast.error('Failed to confirm connection.');
    }
  };

  const handleRevokeConnection = async (id: string) => {
    try {
      await api.post('/parent-link/revoke', { parent_link_id: id });
      toast.success('Parent access revoked.');
      fetchConnections();
    } catch (e) {
      toast.error('Failed to revoke connection.');
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header>
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">
          Parent Connect Dashboard
        </h2>
        <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">
          Enable or revoke weekly progress summaries shared with parent advocates via double-consent SMS/WhatsApp
        </p>
      </header>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Link Request Form */}
        <div className="glass-panel p-6 rounded-3xl space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Connect Parent/Guardian</h3>
          
          <form onSubmit={handleRequestLink} className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Parent / Guardian Name</label>
              <input
                type="text"
                placeholder="Parent name..."
                value={parentName}
                onChange={(e) => setParentName(e.target.value)}
                className="w-full px-4 py-3 bg-slate-950 border border-slate-800 focus:border-primary rounded-2xl text-white outline-none text-sm"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">WhatsApp Phone Number</label>
              <input
                type="text"
                placeholder="e.g. +919876543210..."
                value={parentPhone}
                onChange={(e) => setParentPhone(e.target.value)}
                className="w-full px-4 py-3 bg-slate-950 border border-slate-800 focus:border-primary rounded-2xl text-white outline-none text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={submitting || !parentName.trim() || !parentPhone.trim()}
              className="w-full py-3 bg-primary hover:bg-primary-hover text-slate-950 font-bold rounded-2xl text-xs transition flex justify-center items-center gap-2"
            >
              {submitting ? 'Sending Request...' : 'Send Invitation'}
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Info Box */}
        <div className="glass-panel p-6 rounded-3xl space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Consent Policy</h3>
            <ul className="space-y-3 text-xs text-slate-400">
              <li className="flex gap-2.5">
                <ShieldCheck className="text-primary w-5 h-5 shrink-0" />
                <span>
                  <strong>Strict Double-Consent:</strong> We never message your parents until you explicitly approve the request here.
                </span>
              </li>
              <li className="flex gap-2.5">
                <ShieldCheck className="text-primary w-5 h-5 shrink-0" />
                <span>
                  <strong>Anonymized Summaries:</strong> We only share general progress statistics (e.g. streaks, completed sessions). We never share full mock transcripts, notes, or cognitive load profiles.
                </span>
              </li>
              <li className="flex gap-2.5">
                <ShieldCheck className="text-primary w-5 h-5 shrink-0" />
                <span>
                  <strong>Revocation:</strong> You hold full control. Revoke consent at any time to instantly block further messaging.
                </span>
              </li>
            </ul>
          </div>
          <div className="pt-4 border-t border-slate-850 flex items-center justify-between text-[11px] text-slate-500 font-bold uppercase tracking-wider">
            <span>Security Layer</span>
            <span className="text-primary">HIPAA/COPPA Compliant</span>
          </div>
        </div>
      </div>

      {/* Active connections list */}
      <div className="glass-panel p-6 rounded-3xl space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Consent Relationships</h3>

        {isLoading ? (
          <div className="flex justify-center py-6">
            <div className="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
          </div>
        ) : connections.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs border border-dashed border-slate-850 rounded-2xl">
            No parent links configured. Add your parent above to share your journey.
          </div>
        ) : (
          <div className="divide-y divide-slate-850">
            {connections.map((conn) => (
              <div key={conn.id} className="flex justify-between items-center py-4 first:pt-0 last:pb-0">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{conn.parent_name}</span>
                    <span className="text-slate-400 text-xs font-mono">{conn.parent_phone}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                      conn.consent_status === 'active'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25'
                        : conn.consent_status === 'pending'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/25'
                        : 'bg-slate-900 text-slate-400 border border-slate-800'
                    }`}>
                      {conn.consent_status}
                    </span>
                    <span className="text-[10px] text-slate-500">
                      Requested {new Date(conn.consent_requested_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  {conn.consent_status === 'pending' && (
                    <button
                      onClick={() => handleConfirmConnection(conn.id)}
                      className="px-3 py-1.5 bg-primary text-slate-950 text-xs font-bold rounded-xl hover:bg-primary-hover transition"
                    >
                      Approve Link
                    </button>
                  )}
                  {conn.consent_status === 'active' && (
                    <button
                      onClick={() => handleRevokeConnection(conn.id)}
                      className="px-3 py-1.5 bg-rose-500/10 border border-rose-500/25 text-rose-400 hover:bg-rose-500/20 text-xs font-bold rounded-xl transition"
                    >
                      Revoke
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
export default ParentConnect;
