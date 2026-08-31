import { useState, useEffect } from 'react';
import { Crown, ChevronUp, Trophy, Sparkles, Flame, Users, ArrowUpRight, Search, Filter } from 'lucide-react';
import client from '@/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Link } from 'react-router-dom';

const LEADERBOARDS = {
  global: [
    { rank: 1, name: 'Arjun Mehta', xp: 14850, level: 19, streak: 52, badge: '👑', change: 0, role: 'Google L4 SDE Ready', college: 'IIT Bombay' },
    { rank: 2, name: 'Priya Sharma', xp: 12900, level: 18, streak: 41, badge: '🥈', change: 1, role: 'Flipkart SDE-2 Offer', college: 'BITS Pilani' },
    { rank: 3, name: 'Rohit Kumar', xp: 11400, level: 16, streak: 33, badge: '🥉', change: -1, role: 'Amazon SDE-1 Final', college: 'DTU Delhi' },
    { rank: 4, name: 'Sneha Patel', xp: 10150, level: 15, streak: 28, badge: '🎯', change: 2, role: 'Stripe Backend Track', college: 'NIT Trichy' },
    { rank: 5, name: 'Vivek Singh', xp: 9200, level: 14, streak: 22, badge: '⚡', change: 0, role: 'Swiggy Platform Track', college: 'VTU Bengaluru' },
    { rank: 6, name: 'Demo Candidate (You)', xp: 2150, level: 8, streak: 14, badge: '🔥', change: 3, role: 'Full-Stack MNC Track', college: 'Vireoniq Candidate' },
    { rank: 7, name: 'Ananya Roy', xp: 1950, level: 7, streak: 11, badge: '⭐', change: 1, role: 'Zepto Core Systems', college: 'Anna University' },
    { rank: 8, name: 'Kabir Das', xp: 1800, level: 7, streak: 9, badge: '⭐', change: -2, role: 'Razorpay FinTech', college: 'AKTU Lucknow' }
  ],
  weekly: [
    { rank: 1, name: 'Demo Candidate (You)', xp: 450, level: 8, streak: 14, badge: '👑', change: 4, role: 'Active Sprint', college: 'Vireoniq Candidate' },
    { rank: 2, name: 'Arjun Mehta', xp: 420, level: 19, streak: 52, badge: '🥈', change: -1, role: 'Google L4 SDE Ready', college: 'IIT Bombay' },
    { rank: 3, name: 'Sneha Patel', xp: 380, level: 15, streak: 28, badge: '🥉', change: 1, role: 'Stripe Backend Track', college: 'NIT Trichy' },
    { rank: 4, name: 'Priya Sharma', xp: 310, level: 18, streak: 41, badge: '🎯', change: -2, role: 'Flipkart SDE-2 Offer', college: 'BITS Pilani' },
    { rank: 5, name: 'Rohit Kumar', xp: 290, level: 16, streak: 33, badge: '⚡', change: 0, role: 'Amazon SDE-1 Final', college: 'DTU Delhi' }
  ],
  role: [
    { rank: 1, name: 'Arjun Mehta', xp: 14850, level: 19, streak: 52, badge: '👑', change: 0, role: 'Systems & Cloud', college: 'IIT Bombay' },
    { rank: 2, name: 'Sneha Patel', xp: 10150, level: 15, streak: 28, badge: '🥈', change: 2, role: 'Systems & Cloud', college: 'NIT Trichy' },
    { rank: 3, name: 'Demo Candidate (You)', xp: 2150, level: 8, streak: 14, badge: '🥉', change: 1, role: 'Systems & Cloud', college: 'Vireoniq Candidate' },
    { rank: 4, name: 'Vivek Singh', xp: 9200, level: 14, streak: 22, badge: '⚡', change: 0, role: 'Systems & Cloud', college: 'VTU Bengaluru' }
  ]
};

export const LeaderboardPage = () => {
  const [tab, setTab] = useState<'global' | 'weekly' | 'role'>('global');
  const [search, setSearch] = useState('');
  const [leaderboardData, setLeaderboardData] = useState<any[]>(LEADERBOARDS.global);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const res = await client.get(`/gamification/leaderboard/${tab}`);
        const list = Array.isArray(res.data) ? res.data : (res.data?.rankings || []);
        if (list.length > 0 && list[0].name) {
          setLeaderboardData(list);
        } else {
          setLeaderboardData(LEADERBOARDS[tab]);
        }
      } catch (e) {
        setLeaderboardData(LEADERBOARDS[tab]);
      }
    };
    fetchLeaderboard();
  }, [tab]);

  const filtered = leaderboardData.filter((entry) => {
    if (!search) return true;
    const s = search.toLowerCase();
    const matchName = entry.name ? entry.name.toLowerCase().includes(s) : false;
    const matchRole = entry.role ? entry.role.toLowerCase().includes(s) : false;
    const matchCollege = entry.college ? entry.college.toLowerCase().includes(s) : false;
    return matchName || matchRole || matchCollege;
  });

  return (
    <div className="space-y-8 animate-fade-in pb-20">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-yellow-400 tracking-wide uppercase mb-1">
            <Sparkles className="w-3.5 h-3.5" /> Peer Benchmark & Rankings
          </div>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center text-yellow-400 shadow-lg shadow-yellow-500/10">
              <Crown className="w-5 h-5" />
            </div>
            Global Candidate Leaderboard
          </h1>
          <p className="text-slate-400 mt-1 text-sm max-w-xl">
            Live competitive ranking based on verified problem solving, active recall consistency, and micro-internship completions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/app/gamification">
            <Button variant="outline" className="rounded-xl border-white/10 text-slate-300 hover:text-white text-xs font-bold py-5">
              <Trophy className="w-4 h-4 mr-1.5 text-yellow-400" /> My Badges & XP Hub
            </Button>
          </Link>
        </div>
      </header>

      {/* Tabs & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900/60 p-4 rounded-2xl border border-white/5 shadow-xl">
        <div className="flex gap-1.5 w-full sm:w-auto">
          {[
            { id: 'global', label: 'All-Time Global' },
            { id: 'weekly', label: 'Weekly Sprint' },
            { id: 'role', label: 'Target Role (Backend/Systems)' }
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id as any)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shrink-0 ${
                tab === t.id
                  ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/40 shadow-sm'
                  : 'bg-slate-950 text-slate-400 hover:text-white border border-white/5'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="w-full sm:w-64 relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search candidates, colleges..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-white outline-none focus:border-yellow-500/50"
          />
        </div>
      </div>

      {/* Leaderboard Table Card */}
      <Card className="bg-slate-950 border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
        <div className="p-5 border-b border-white/5 flex items-center justify-between bg-slate-900/40 text-xs font-bold text-slate-400 uppercase tracking-widest">
          <div className="flex items-center gap-6">
            <span className="w-12 text-center">Rank</span>
            <span>Candidate & Target Milestone</span>
          </div>
          <span>Experience & Consistency</span>
        </div>

        <div className="divide-y divide-white/5">
          {filtered.map((entry) => {
            const isMe = entry.name.includes('You');
            return (
              <div
                key={entry.rank}
                className={`flex items-center justify-between p-4 sm:p-5 transition-all hover:bg-white/5 ${
                  isMe ? 'bg-cyan-500/10 border-l-4 border-l-cyan-400' : ''
                }`}
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 text-center font-black">
                    {entry.rank <= 3 ? (
                      <span className="text-2xl">{entry.badge}</span>
                    ) : (
                      <span className="text-sm text-slate-500 font-bold">#{entry.rank}</span>
                    )}
                  </div>

                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-cyan-500 flex items-center justify-center text-white font-black text-xs shadow-md">
                    {entry.name[0]}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <p className={`font-black text-sm ${isMe ? 'text-cyan-300' : 'text-slate-100'}`}>
                        {entry.name}
                      </p>
                      {isMe && (
                        <Badge className="bg-cyan-500/20 text-cyan-300 border-cyan-500/30 text-[9px] font-bold px-1.5 py-0">
                          YOU
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 font-medium mt-0.5">
                      {entry.role} • <span className="text-slate-500">{entry.college}</span>
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-right">
                  <div>
                    <p className="text-sm font-black text-yellow-400 font-mono">
                      {entry.xp.toLocaleString()} XP
                    </p>
                    <p className="text-[11px] text-slate-500 font-medium">
                      Lv.{entry.level} • {entry.streak}d streak 🔥
                    </p>
                  </div>
                  {entry.change > 0 && (
                    <div className="flex items-center text-emerald-400 text-xs font-bold">
                      <ChevronUp className="w-4 h-4" />
                      <span>{entry.change}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};
