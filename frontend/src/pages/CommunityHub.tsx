import React, { useState, useEffect } from "react";
import {
  Code2, Users2, Trophy, MessageSquare, Clock, Zap, ChevronRight,
  Flame, Target, Globe, Heart, Share2, Star, Timer, Play
} from "lucide-react";
import { Button } from "@/components/ui/button";
import client from "@/api/client";
import { toast } from "sonner";

interface Challenge {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  category: string;
  time_limit_minutes: number;
  xp_reward: number;
  participants_count: number;
  hints: string[];
  solution_template: string;
}

interface StudyGroup {
  id: string;
  name: string;
  description: string;
  target_role: string;
  timezone: string;
  language: string;
  max_members: number;
  current_members: number;
}

interface Post {
  id: string;
  user_id: string;
  post_type: string;
  title: string;
  content: string;
  likes_count: number;
  created_at: string;
}

type Tab = "challenge" | "groups" | "feed";

const difficultyColors: Record<string, string> = {
  easy: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  medium: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  hard: "text-rose-400 bg-rose-500/10 border-rose-500/20",
};

const DEFAULT_CHALLENGE: Challenge = {
  id: "chal-daily-01",
  title: "Longest Substring Without Repeating Characters",
  description: "Given a string `s`, find the length of the **longest substring** without repeating characters.\n\n### Example 1:\n```\nInput: s = \"abcabcbb\"\nOutput: 3\nExplanation: The answer is \"abc\", with the length of 3.\n```\n\n### Constraints:\n- `0 <= s.length <= 5 * 10^4`\n- `s` consists of English letters, digits, symbols and spaces.",
  difficulty: "medium",
  category: "dsa",
  time_limit_minutes: 30,
  xp_reward: 50,
  participants_count: 248,
  hints: [
    "Use the sliding window technique with two pointers (left and right).",
    "Maintain a hash set or dictionary of characters in the current window.",
    "When a duplicate is encountered, shrink the window from the left until the duplicate is removed."
  ],
  solution_template: `def length_of_longest_substring(s: str) -> int:
    char_map = {}
    max_len = 0
    left = 0
    
    for right, ch in enumerate(s):
        if ch in char_map and char_map[ch] >= left:
            left = char_map[ch] + 1
        char_map[ch] = right
        max_len = max(max_len, right - left + 1)
        
    return max_len`
};

const DEFAULT_STUDY_GROUPS: StudyGroup[] = [
  {
    id: "grp-01",
    name: "FAANG System Design Masters",
    description: "Deep dive into distributed systems, scale architectures, and bar-raiser mock interviews.",
    target_role: "Backend Engineer",
    timezone: "IST (UTC+5:30)",
    language: "en",
    max_members: 6,
    current_members: 4
  },
  {
    id: "grp-02",
    name: "LeetCode Daily 100 Hard Club",
    description: "Daily timed problem solving focusing on Graphs, DP, and Segment Trees.",
    target_role: "Software Engineer",
    timezone: "IST (UTC+5:30)",
    language: "en",
    max_members: 8,
    current_members: 6
  },
  {
    id: "grp-03",
    name: "Full-Stack AI Innovators",
    description: "Building production React + FastAPI AI copilot apps and sharing code reviews.",
    target_role: "Full-Stack Engineer",
    timezone: "IST (UTC+5:30)",
    language: "en",
    max_members: 6,
    current_members: 3
  }
];

const DEFAULT_COMMUNITY_POSTS: Post[] = [
  {
    id: "post-01",
    user_id: "usr-01",
    post_type: "offer_received",
    title: "Cracked Google L4 SWE! 🎉",
    content: "Huge thanks to VIREONIQ's mock studio and career twin. The distributed systems bottleneck diagnostics directly matched Round 3!",
    likes_count: 84,
    created_at: new Date(Date.now() - 3600000 * 4).toISOString()
  },
  {
    id: "post-02",
    user_id: "usr-02",
    post_type: "streak_milestone",
    title: "30-Day Daily Career OS Streak Achieved! 🔥",
    content: "Maintained 3 tasks/day consistency. My PRS score increased from 58 to 86 in 4 weeks.",
    likes_count: 42,
    created_at: new Date(Date.now() - 3600000 * 12).toISOString()
  },
  {
    id: "post-03",
    user_id: "usr-03",
    post_type: "challenge_win",
    title: "Solved Today's Concurrency Lock Challenge in 14 mins! ⚡",
    content: "Used Redis Redlock algorithm pattern. Check the hint for the sliding window TTL trick.",
    likes_count: 29,
    created_at: new Date(Date.now() - 3600000 * 20).toISOString()
  }
];

const CommunityHub = () => {
  const [activeTab, setActiveTab] = useState<Tab>("challenge");
  const [challenge, setChallenge] = useState<Challenge | null>(DEFAULT_CHALLENGE);
  const [groups, setGroups] = useState<StudyGroup[]>(DEFAULT_STUDY_GROUPS);
  const [posts, setPosts] = useState<Post[]>(DEFAULT_COMMUNITY_POSTS);
  const [isLoading, setIsLoading] = useState(false);
  const [solutionCode, setSolutionCode] = useState(DEFAULT_CHALLENGE.solution_template);
  const [showHints, setShowHints] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);

  useEffect(() => {
    if (activeTab === "challenge") fetchChallenge();
    if (activeTab === "groups") fetchGroups();
    if (activeTab === "feed") fetchFeed();
  }, [activeTab]);

  useEffect(() => {
    let interval: number;
    if (isTimerRunning) {
      interval = window.setInterval(() => setTimerSeconds(s => s + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  const fetchChallenge = async () => {
    setIsLoading(true);
    try {
      const res = await client.get("/community/challenge/today");
      if (res.data && res.data.title) {
        setChallenge(res.data);
        setSolutionCode(res.data?.solution_template || DEFAULT_CHALLENGE.solution_template);
      } else {
        setChallenge(DEFAULT_CHALLENGE);
        setSolutionCode(DEFAULT_CHALLENGE.solution_template);
      }
    } catch {
      setChallenge(DEFAULT_CHALLENGE);
      setSolutionCode(DEFAULT_CHALLENGE.solution_template);
    } finally { setIsLoading(false); }
  };

  const fetchGroups = async () => {
    setIsLoading(true);
    try {
      const res = await client.get("/community/groups/search");
      if (res.data?.groups && Array.isArray(res.data.groups) && res.data.groups.length > 0) {
        setGroups(res.data.groups);
      } else {
        setGroups(DEFAULT_STUDY_GROUPS);
      }
    } catch {
      setGroups(DEFAULT_STUDY_GROUPS);
    } finally { setIsLoading(false); }
  };

  const fetchFeed = async () => {
    setIsLoading(true);
    try {
      const res = await client.get("/community/feed");
      if (res.data?.posts && Array.isArray(res.data.posts) && res.data.posts.length > 0) {
        setPosts(res.data.posts);
      } else {
        setPosts(DEFAULT_COMMUNITY_POSTS);
      }
    } catch {
      setPosts(DEFAULT_COMMUNITY_POSTS);
    } finally { setIsLoading(false); }
  };

  const submitChallenge = async () => {
    if (!challenge) return;
    try {
      await client.post("/community/challenge/submit", {
        challenge_id: challenge.id,
        solution_code: solutionCode,
        language: "python",
        time_taken_seconds: timerSeconds,
      });
      setIsTimerRunning(false);
      toast.success("Solution submitted! 🎉");
    } catch {
      toast.error("Failed to submit solution");
    }
  };

  const joinGroup = async (groupId: string) => {
    try {
      await client.post(`/community/groups/${groupId}/join`);
      toast.success("Joined study group! 🤝");
      fetchGroups();
    } catch {
      toast.error("Failed to join group");
    }
  };

  const likePost = async (postId: string) => {
    try {
      await client.post(`/community/feed/${postId}/like`);
      setPosts(prev => prev.map(p => p.id === postId ? { ...p, likes_count: p.likes_count + 1 } : p));
    } catch {
      toast.error("Failed to like post");
    }
  };

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const tabs: { key: Tab; label: string; icon: React.ElementType }[] = [
    { key: "challenge", label: "Daily Challenge", icon: Code2 },
    { key: "groups", label: "Study Groups", icon: Users2 },
    { key: "feed", label: "Community Feed", icon: MessageSquare },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Header */}
      <header>
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-primary/10 border border-primary/20 rounded-full text-xs font-bold text-primary uppercase tracking-wider mb-4">
          <Flame className="w-4 h-4" /> Community Hub
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-white to-slate-400 bg-clip-text text-transparent">
          Learn Together, Grow Together
        </h1>
        <p className="text-slate-400 mt-2 text-sm max-w-xl">
          Compete in daily challenges, join study groups with peers in your timezone, and celebrate each other's wins.
        </p>
      </header>

      {/* Tabs */}
      <div className="flex gap-2">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 border ${
              activeTab === tab.key
                ? "bg-gradient-to-r from-primary/20 to-accent/20 text-white border-white/10 shadow-lg shadow-primary/10"
                : "text-slate-400 border-transparent hover:text-white hover:bg-white/5"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Daily Challenge Tab */}
      {activeTab === "challenge" && (
        <div className="space-y-6">
          {isLoading ? (
            <div className="glass-panel rounded-3xl p-12 text-center">
              <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto" />
              <p className="text-sm text-slate-500 mt-4">Generating today's challenge…</p>
            </div>
          ) : challenge ? (
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Challenge Details */}
              <div className="lg:col-span-2 glass-panel rounded-3xl p-8 space-y-6">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-xl font-bold text-white">{challenge.title}</h2>
                      <span className={`px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-full border ${difficultyColors[challenge.difficulty]}`}>
                        {challenge.difficulty}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span className="flex items-center gap-1"><Target className="w-3 h-3" />{challenge.category.toUpperCase()}</span>
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{challenge.time_limit_minutes} min</span>
                      <span className="flex items-center gap-1"><Zap className="w-3 h-3" />{challenge.xp_reward} XP</span>
                      <span className="flex items-center gap-1"><Users2 className="w-3 h-3" />{challenge.participants_count} solved</span>
                    </div>
                  </div>
                </div>

                <div className="prose prose-invert prose-sm max-w-none text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {challenge.description}
                </div>

                {/* Code Editor */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Your Solution</label>
                    <div className="flex items-center gap-3">
                      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-mono font-bold ${isTimerRunning ? "bg-emerald-500/10 text-emerald-400" : "bg-white/5 text-slate-400"}`}>
                        <Timer className="w-3.5 h-3.5" />
                        {formatTime(timerSeconds)}
                      </div>
                      <Button size="sm" variant="outline" onClick={() => { setIsTimerRunning(!isTimerRunning); if (!isTimerRunning) setTimerSeconds(0); }}>
                        <Play className="w-3 h-3 mr-1" />
                        {isTimerRunning ? "Pause" : "Start"}
                      </Button>
                    </div>
                  </div>
                  <textarea
                    value={solutionCode}
                    onChange={e => setSolutionCode(e.target.value)}
                    className="w-full h-64 bg-black/40 border border-white/10 rounded-xl p-4 text-sm font-mono text-slate-200 resize-none focus:outline-none focus:ring-2 focus:ring-primary/40"
                    placeholder="Write your solution here..."
                  />
                </div>

                <div className="flex items-center gap-3">
                  <Button onClick={submitChallenge} className="bg-gradient-to-r from-primary to-accent hover:opacity-90">
                    <Zap className="w-4 h-4 mr-2" /> Submit Solution
                  </Button>
                  <Button variant="outline" onClick={() => setShowHints(!showHints)}>
                    💡 {showHints ? "Hide" : "Show"} Hints
                  </Button>
                </div>

                {showHints && challenge.hints?.length > 0 && (
                  <div className="space-y-2">
                    {challenge.hints.map((hint, idx) => (
                      <div key={idx} className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-3 text-sm text-amber-200">
                        <span className="font-bold text-amber-400">Hint {idx + 1}:</span> {hint}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Stats Sidebar */}
              <div className="space-y-4">
                <div className="glass-panel rounded-3xl p-6 text-center">
                  <Trophy className="w-10 h-10 text-amber-400 mx-auto mb-3" />
                  <div className="text-3xl font-black text-white">{challenge.participants_count}</div>
                  <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider mt-1">Global Solvers Today</div>
                </div>
                <div className="glass-panel rounded-3xl p-6 text-center">
                  <Flame className="w-10 h-10 text-orange-400 mx-auto mb-3" />
                  <div className="text-3xl font-black text-white">{challenge.xp_reward}</div>
                  <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider mt-1">XP Reward</div>
                </div>
                <div className="glass-panel rounded-3xl p-6">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Share Your Streak</h4>
                  <Button variant="outline" className="w-full" onClick={() => {
                    navigator.clipboard.writeText(`I just solved today's #VIREONIQ challenge! 🔥 Join me: ${window.location.origin}/app/community`);
                    toast.success("Copied share link! 📋");
                  }}>
                    <Share2 className="w-4 h-4 mr-2" /> Copy Share Link
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel rounded-3xl p-12 text-center text-slate-500">No challenge available yet. Check back soon!</div>
          )}
        </div>
      )}

      {/* Study Groups Tab */}
      {activeTab === "groups" && (
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {isLoading ? (
              <div className="col-span-full glass-panel rounded-3xl p-12 text-center">
                <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto" />
              </div>
            ) : groups.length > 0 ? (
              groups.map(group => (
                <div key={group.id} className="glass-panel rounded-2xl p-6 space-y-4 hover:border-primary/20 transition-all duration-300 group/card">
                  <div>
                    <h3 className="text-base font-bold text-white group-hover/card:text-primary transition-colors">{group.name}</h3>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">{group.description}</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-0.5 bg-primary/10 border border-primary/20 rounded-full text-[10px] font-bold text-primary">{group.target_role}</span>
                    <span className="px-2 py-0.5 bg-white/5 border border-white/10 rounded-full text-[10px] font-bold text-slate-400 flex items-center gap-1">
                      <Globe className="w-2.5 h-2.5" />{group.timezone}
                    </span>
                    <span className="px-2 py-0.5 bg-white/5 border border-white/10 rounded-full text-[10px] font-bold text-slate-400">{group.language.toUpperCase()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="text-xs text-slate-400">
                      <span className="text-white font-bold">{group.current_members}</span>/{group.max_members} members
                    </div>
                    <Button size="sm" variant="outline" onClick={() => joinGroup(group.id)} disabled={group.current_members >= group.max_members}>
                      {group.current_members >= group.max_members ? "Full" : "Join"}
                      <ChevronRight className="w-3 h-3 ml-1" />
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full glass-panel rounded-3xl p-12 text-center text-slate-500">
                No study groups found. Be the first to create one!
              </div>
            )}
          </div>
        </div>
      )}

      {/* Community Feed Tab */}
      {activeTab === "feed" && (
        <div className="space-y-4 max-w-2xl">
          {isLoading ? (
            <div className="glass-panel rounded-3xl p-12 text-center">
              <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto" />
            </div>
          ) : posts.length > 0 ? (
            posts.map(post => (
              <div key={post.id} className="glass-panel rounded-2xl p-6 space-y-3 hover:border-primary/10 transition-all duration-300">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 bg-primary/10 border border-primary/20 rounded-full text-[10px] font-bold text-primary capitalize">{post.post_type.replace("_", " ")}</span>
                    </div>
                    <h3 className="text-base font-bold text-white">{post.title}</h3>
                  </div>
                  <span className="text-[10px] text-slate-500">{new Date(post.created_at).toLocaleDateString()}</span>
                </div>
                {post.content && <p className="text-sm text-slate-400">{post.content}</p>}
                <div className="flex items-center gap-4 pt-2 border-t border-white/5">
                  <button onClick={() => likePost(post.id)} className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-rose-400 transition-colors">
                    <Heart className="w-3.5 h-3.5" /> {post.likes_count}
                  </button>
                  <button className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-primary transition-colors">
                    <Share2 className="w-3.5 h-3.5" /> Share
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="glass-panel rounded-3xl p-12 text-center text-slate-500">
              <Star className="w-8 h-8 mx-auto mb-3 text-slate-600" />
              <p>No posts yet. Complete a challenge to share your first achievement!</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CommunityHub;
