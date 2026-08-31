import { useState, useEffect } from 'react';
import { Trophy, Flame, Zap, Award, Users, Crown, CheckCircle2, Sparkles, ArrowRight } from 'lucide-react';
import client from "@/api/client";
import { toast } from "sonner";
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const BADGES = [
  { id: 'first_interview', name: 'First Interview', icon: '🎯', earned: true, category: 'milestone', xp: 300, desc: 'Completed first AI Bar-Raiser mock' },
  { id: 'streak_7', name: '7-Day Streak', icon: '🔥', earned: true, category: 'streak', xp: 200, desc: 'Maintained active recall practice for 7 consecutive days' },
  { id: 'streak_30', name: '30-Day Streak', icon: '⚡', earned: false, category: 'streak', xp: 500, desc: 'Consistent 30-day prep cycle' },
  { id: 'micro_intern', name: 'Verified Builder', icon: '🛡️', earned: true, category: 'internship', xp: 250, desc: 'Passed industry-standard micro-internship task' },
  { id: 'level_5', name: 'Level 5 Achieved', icon: '💎', earned: true, category: 'performance', xp: 150, desc: 'Earned 1,500+ XP across all modules' },
  { id: 'top_100', name: 'Top 100 Global', icon: '👑', earned: false, category: 'social', xp: 600, desc: 'Ranked in the top 100 globally' },
];

const LEVEL_THRESHOLDS = [0, 100, 300, 600, 1000, 1500, 2200, 3100, 4200, 5500, 7000];

export const GamificationPage = () => {
  const [profile, setProfile] = useState(() => {
    const saved = localStorage.getItem("vireoniq_gamification_profile");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {}
    }
    return {
      total_xp: 2150,
      weekly_xp: 450,
      current_level: 8,
      current_streak_days: 14,
      longest_streak_days: 21,
      rank_global: 184,
      rank_weekly: 42,
      earned_badges: ['first_interview', 'streak_7', 'micro_intern', 'level_5'],
      daily_claimed: false
    };
  });

  useEffect(() => {
    const fetchGamification = async () => {
      try {
        const res = await client.get("/gamification/profile");
        if (res.data && res.data.total_xp) {
          setProfile((prev: any) => ({
            ...prev,
            ...res.data
          }));
        }
      } catch (e) {}
    };
    fetchGamification();
  }, []);

  const handleClaimDaily = async () => {
    if (profile.daily_claimed) {
      toast.info("Daily check-in streak already claimed for today!");
      return;
    }

    try {
      await client.post("/gamification/award-xp", {
        event: "daily_checkin",
        custom_xp: 50
      });
    } catch (e) {}

    const updated = {
      ...profile,
      total_xp: profile.total_xp + 50,
      weekly_xp: profile.weekly_xp + 50,
      current_streak_days: profile.current_streak_days + 1,
      daily_claimed: true
    };
    setProfile(updated);
    localStorage.setItem("vireoniq_gamification_profile", JSON.stringify(updated));
    toast.success("🔥 Daily Check-in Streak Claimed! +50 XP Awarded!");
  };

  const currentThreshold = LEVEL_THRESHOLDS[profile.current_level - 1] || 0;
  const nextThreshold = LEVEL_THRESHOLDS[profile.current_level] || LEVEL_THRESHOLDS[LEVEL_THRESHOLDS.length - 1];
  const xpProgress = Math.min(100, Math.max(0, ((profile.total_xp - currentThreshold) / (nextThreshold - currentThreshold)) * 100));

  return (
    <div className="space-y-8 animate-fade-in pb-20">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-amber-400 tracking-wide uppercase mb-1">
            <Sparkles className="w-3.5 h-3.5" /> Rewards & Recognition
          </div>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center text-yellow-400 shadow-lg shadow-yellow-500/10">
              <Trophy className="w-5 h-5" />
            </div>
            Gamification Hub
          </h1>
          <p className="text-slate-400 mt-1 text-sm max-w-xl">
            Track your verified XP gains, practice streaks, unlocked achievements, and global candidate ranking.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={handleClaimDaily}
            className={`rounded-xl text-xs font-bold py-5 shadow-lg ${
              profile.daily_claimed
                ? "bg-slate-900 border border-white/10 text-slate-400 cursor-not-allowed"
                : "bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 hover:to-amber-400 text-white shadow-orange-500/20"
            }`}
          >
            <Flame className="w-4 h-4 mr-1.5 text-yellow-300" />
            {profile.daily_claimed ? "Streak Maintained Today ✓" : "Claim Daily Streak (+50 XP)"}
          </Button>

          <Link to="/app/leaderboard">
            <Button variant="outline" className="rounded-xl border-white/10 text-slate-300 hover:text-white text-xs font-bold py-5">
              <Crown className="w-4 h-4 mr-1.5 text-yellow-400" /> Global Leaderboard
            </Button>
          </Link>
        </div>
      </header>

      {/* XP & Level Bar */}
      <div className="bg-gradient-to-r from-indigo-950/80 via-slate-950 to-cyan-950/80 border border-indigo-500/30 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1">
              Current Competency Tier
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl sm:text-5xl font-black text-white">Level {profile.current_level}</span>
              <span className="text-slate-500 text-xs font-bold uppercase tracking-wider">Senior Candidate Track</span>
            </div>
          </div>
          <div className="text-left sm:text-right">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1">
              Accumulated Experience
            </span>
            <div className="text-2xl sm:text-3xl font-black text-yellow-400">
              {profile.total_xp.toLocaleString()} XP
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="h-3.5 bg-slate-900/90 rounded-full overflow-hidden p-0.5 border border-white/5">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 rounded-full shadow-[0_0_20px_rgba(99,102,241,0.6)] transition-all duration-700"
              style={{ width: `${xpProgress}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-slate-400 font-medium">
            <span>Level {profile.current_level} ({currentThreshold} XP)</span>
            <span className="text-cyan-400 font-bold">{Math.round(xpProgress)}% towards Level {profile.current_level + 1}</span>
            <span>{nextThreshold} XP Goal</span>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Weekly XP Gain', value: `+${profile.weekly_xp} XP`, icon: Zap, color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
          { label: 'Current Practice Streak', value: `${profile.current_streak_days} Days`, icon: Flame, color: 'text-orange-400', bg: 'bg-orange-400/10' },
          { label: 'Global Ranking', value: `#${profile.rank_global}`, icon: Crown, color: 'text-purple-400', bg: 'bg-purple-400/10' },
          { label: 'Weekly Cohort Rank', value: `#${profile.rank_weekly}`, icon: Users, color: 'text-cyan-400', bg: 'bg-cyan-400/10' },
        ].map((s, i) => (
          <div key={i} className="bg-slate-950 border border-white/10 rounded-2xl p-5 flex flex-col justify-between shadow-xl">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{s.label}</span>
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${s.bg}`}>
                <s.icon className={`w-4 h-4 ${s.color}`} />
              </div>
            </div>
            <p className={`text-2xl font-black ${s.color} mt-3`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Badges Matrix */}
      <div className="bg-slate-950 border border-white/10 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-black text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-yellow-400" /> Verified Candidate Badges
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Badges directly visible to partner recruiters on your Talent Passport.
            </p>
          </div>
          <Badge variant="outline" className="text-xs border-white/10 text-slate-400">
            {profile.earned_badges?.length || 4} of {BADGES.length} Unlocked
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {BADGES.map((badge) => {
            const isEarned = profile.earned_badges?.includes(badge.id);
            return (
              <div
                key={badge.id}
                className={`p-4 rounded-2xl border transition-all flex items-start gap-3.5 ${
                  isEarned
                    ? 'border-indigo-500/40 bg-indigo-500/10 shadow-[0_0_20px_rgba(99,102,241,0.15)]'
                    : 'border-white/5 bg-slate-900/40 opacity-50 grayscale'
                }`}
              >
                <div className="text-3xl shrink-0 p-2 bg-slate-900 rounded-xl border border-white/5">
                  {badge.icon}
                </div>
                <div className="space-y-1 flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-black text-white">{badge.name}</h4>
                    <span className="text-[10px] font-bold text-yellow-400">+{badge.xp} XP</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{badge.desc}</p>
                  <div className="pt-1">
                    {isEarned ? (
                      <span className="text-[10px] font-bold text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Unlocked & Verified
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold text-slate-500">Locked</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
